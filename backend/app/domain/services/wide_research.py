import asyncio
import csv
import io
import json
import logging
import re
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable, Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import get_settings
from app.domain.external.file import FileStorage
from app.domain.external.search import SearchEngine
from app.domain.models.agent import Agent
from app.domain.models.event import (
    BaseEvent,
    WideResearchCompleteEvent,
    WideResearchSubjectCompleteEvent,
    WideResearchSubjectsIdentifiedEvent,
)
from app.domain.models.file import FileInfo
from app.domain.repositories.session_repository import SessionRepository

logger = logging.getLogger(__name__)


class WideResearchService:
    def __init__(
        self,
        agent: Agent,
        session_id: str,
        user_id: str,
        file_storage: FileStorage,
        session_repository: SessionRepository,
        search_engine: Optional[SearchEngine] = None,
    ):
        self._agent = agent
        self._session_id = session_id
        self._user_id = user_id
        self._file_storage = file_storage
        self._session_repository = session_repository
        self._search_engine = search_engine
        self._model = self._build_model()

    def _build_model(self):
        settings = get_settings()
        kwargs: dict[str, Any] = dict(
            model=self._agent.model_name,
            model_provider=settings.model_provider,
            temperature=self._agent.temperature,
            max_tokens=self._agent.max_tokens,
            base_url=settings.api_base,
        )
        if settings.extra_headers:
            kwargs["default_headers"] = settings.extra_headers
        return init_chat_model(**kwargs)

    async def _invoke(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._model.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        content = getattr(response, "content", "")
        if isinstance(content, list):
            return "\n".join(str(item) for item in content)
        return str(content or "")

    def _parse_json_block(self, text: str, fallback: Any) -> Any:
        try:
            return json.loads(text)
        except Exception:
            pass
        match = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        return fallback

    async def identify_subjects(self, query: str) -> list[str]:
        system_prompt = (
            "You identify the best research subject buckets for a broad investigation. "
            "Return JSON only as an array of 3-7 concise subject strings."
        )
        raw = await self._invoke(system_prompt, query)
        subjects = self._parse_json_block(raw, [])
        if isinstance(subjects, list):
            normalized = [str(item).strip() for item in subjects if str(item).strip()]
            if normalized:
                return normalized[:7]
        fallback = [piece.strip() for piece in re.split(r",| and ", query) if piece.strip()]
        if len(fallback) >= 3:
            return fallback[:7]
        return [
            f"{query} market landscape",
            f"{query} competitors",
            f"{query} pricing and packaging",
            f"{query} capabilities and workflows",
            f"{query} customer fit",
        ]

    async def research_subject(self, subject: str, browser=None) -> dict[str, Any]:
        search_packets: list[dict[str, str]] = []
        if self._search_engine:
            queries = [subject, f"{subject} pricing", f"{subject} features"]
            for query in queries:
                try:
                    result = await self._search_engine.search(query)
                    for item in (result.data.results if result and result.data else [])[:4]:
                        search_packets.append(
                            {
                                "title": item.title,
                                "link": item.link,
                                "snippet": item.snippet,
                            }
                        )
                except Exception as exc:
                    logger.warning("Wide research search failed for %s: %s", query, exc)

        system_prompt = (
            "You are a meticulous research analyst. Using the supplied search snippets, synthesize a compact JSON object "
            "with keys name, description, capabilities, pricing, pros_cons, usp, and sources. "
            "pros_cons must contain pros and cons arrays. capabilities and sources must be arrays."
        )
        user_prompt = json.dumps(
            {
                "subject": subject,
                "search_results": search_packets[:10],
            },
            ensure_ascii=False,
        )
        raw = await self._invoke(system_prompt, user_prompt)
        data = self._parse_json_block(raw, {})
        if not isinstance(data, dict):
            data = {}

        sources = data.get("sources")
        if not isinstance(sources, list):
            sources = [item["link"] for item in search_packets[:5]]

        pros_cons = data.get("pros_cons")
        if not isinstance(pros_cons, dict):
            pros_cons = {"pros": [], "cons": []}

        capabilities = data.get("capabilities")
        if not isinstance(capabilities, list):
            capabilities = []

        return {
            "name": str(data.get("name") or subject),
            "description": str(data.get("description") or f"Research summary for {subject}."),
            "capabilities": [str(item) for item in capabilities[:6]],
            "pricing": str(data.get("pricing") or "Varies by use case / plan"),
            "pros_cons": {
                "pros": [str(item) for item in (pros_cons.get("pros") or [])[:4]],
                "cons": [str(item) for item in (pros_cons.get("cons") or [])[:4]],
            },
            "usp": str(data.get("usp") or f"Strong differentiated angle around {subject}."),
            "sources": [str(item) for item in sources[:6]],
        }

    async def _upload_session_file(
        self,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> FileInfo:
        buffer = io.BytesIO(content)
        file_info = await self._file_storage.upload_file(
            buffer,
            filename,
            self._user_id,
            content_type=content_type,
            metadata=metadata or {},
        )
        await self._session_repository.add_file(self._session_id, file_info)
        return file_info

    async def _compile_report(self, query: str, subjects: list[dict[str, Any]]) -> str:
        system_prompt = (
            "Write a comprehensive research report in markdown. Use a strong executive summary, one section per subject, "
            "a comparison table, key findings, and next steps. Cite source URLs inline as bullet references."
        )
        user_prompt = json.dumps({"query": query, "subjects": subjects}, ensure_ascii=False)
        report = await self._invoke(system_prompt, user_prompt)
        return report.strip() or f"# Research report\n\nNo report content generated for {query}."

    async def run_wide_research(
        self,
        query: str,
        emit_progress: Callable[[BaseEvent], Awaitable[None]],
    ) -> tuple[str, list[FileInfo], list[dict[str, Any]]]:
        subjects = await self.identify_subjects(query)
        await emit_progress(
            WideResearchSubjectsIdentifiedEvent(
                query=query,
                subjects=subjects,
            )
        )

        completed = 0

        async def worker(index: int, subject_name: str) -> dict[str, Any]:
            nonlocal completed
            data = await self.research_subject(subject_name)
            completed += 1
            await emit_progress(
                WideResearchSubjectCompleteEvent(
                    query=query,
                    index=index,
                    total=len(subjects),
                    completed=completed,
                    subject=data,
                )
            )
            return data

        results = await asyncio.gather(*(worker(index, subject) for index, subject in enumerate(subjects)))
        report = await self._compile_report(query, results)

        date_stamp = datetime.now(UTC).strftime("%Y%m%d")
        slug = re.sub(r"[^a-z0-9]+", "_", query.lower()).strip("_")[:32] or "topic"

        json_file = await self._upload_session_file(
            f"research_{slug}_{date_stamp}.json",
            json.dumps(results, indent=2, ensure_ascii=False).encode("utf-8"),
            "application/json",
            metadata={"kind": "wide_research_json", "query": query},
        )

        csv_stream = io.StringIO()
        writer = csv.DictWriter(
            csv_stream,
            fieldnames=["Subject", "Description", "Key Capabilities", "Pricing", "Pros", "Cons", "USP"],
        )
        writer.writeheader()
        for row in results:
            writer.writerow(
                {
                    "Subject": row.get("name", ""),
                    "Description": row.get("description", ""),
                    "Key Capabilities": ", ".join(row.get("capabilities", [])),
                    "Pricing": row.get("pricing", ""),
                    "Pros": ", ".join(row.get("pros_cons", {}).get("pros", [])),
                    "Cons": ", ".join(row.get("pros_cons", {}).get("cons", [])),
                    "USP": row.get("usp", ""),
                }
            )
        csv_file = await self._upload_session_file(
            f"research_{slug}_{date_stamp}.csv",
            csv_stream.getvalue().encode("utf-8"),
            "text/csv",
            metadata={"kind": "wide_research_csv", "query": query},
        )

        files = [json_file, csv_file]
        await emit_progress(
            WideResearchCompleteEvent(
                query=query,
                report=report,
                files=files,
                subjects=results,
            )
        )
        return report, files, results
