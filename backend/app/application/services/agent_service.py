from typing import AsyncGenerator, Optional, List
import logging
from datetime import datetime
from app.domain.models.session import Session, SessionSummary
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.user_repository import UserRepository

from app.interfaces.schemas.session import ShellViewResponse
from app.interfaces.schemas.file import FileViewResponse
from app.domain.models.agent import Agent
from app.domain.services.agent_domain_service import AgentDomainService
from app.domain.models.event import AgentEvent
from typing import Type
from app.domain.external.sandbox import Sandbox
from app.domain.external.search import SearchEngine
from app.domain.external.file import FileStorage
from app.domain.repositories.agent_repository import AgentRepository
from app.domain.external.task import Task
from app.domain.models.file import FileInfo
from app.core.config import get_settings
from app.domain.repositories.mcp_repository import MCPRepository
from app.domain.models.session import SessionStatus
from app.application.errors.exceptions import BadRequestError

# Set up logger
logger = logging.getLogger(__name__)

class AgentService:
    def __init__(
        self,
        agent_repository: AgentRepository,
        session_repository: SessionRepository,
        user_repository: UserRepository,
        sandbox_cls: Type[Sandbox],
        task_cls: Type[Task],
        file_storage: FileStorage,
        mcp_repository: MCPRepository,
        search_engine: Optional[SearchEngine] = None,
    ):
        logger.info("Initializing AgentService")
        self._agent_repository = agent_repository
        self._session_repository = session_repository
        self._user_repository = user_repository
        self._file_storage = file_storage
        self._agent_domain_service = AgentDomainService(
            self._agent_repository,
            self._session_repository,
            sandbox_cls,
            task_cls,
            file_storage,
            mcp_repository,
            search_engine,
        )
        self._search_engine = search_engine
        self._sandbox_cls = sandbox_cls
    
    async def create_session(
        self,
        user_id: str,
        model_tier: str = "lite",
        prompt: str = "",
        max_budget: int = 0,
        mode: str = "auto",
        permissions: str = "standard",
        wide_research: bool = False,
    ) -> Session:
        logger.info(f"Creating new session for user: {user_id}")
        user = await self._user_repository.get_user_by_id(user_id)
        if not user:
            raise BadRequestError("User not found")
        if (user.credits or 0) <= 0:
            raise BadRequestError("You are out of credits. Please top up to continue.")
        prepared_prompt = self._prepare_prompt(prompt, wide_research)
        estimated_cost = self._estimate_cost(model_tier, prepared_prompt, wide_research)
        resolved_budget = max_budget if (max_budget or 0) > 0 else max(estimated_cost * 2, estimated_cost)
        if resolved_budget > 0 and estimated_cost > resolved_budget:
            raise BadRequestError(f"This run is estimated at {estimated_cost} credits, which exceeds your budget cap of {resolved_budget}.")
        if (user.credits or 0) < estimated_cost:
            raise BadRequestError(f"You need {estimated_cost} credits for this run but only have {user.credits or 0} left.")
        await self._charge_credits(user_id, estimated_cost)
        agent = await self._create_agent(model_tier=model_tier)
        memory_brief = await self._build_memory_brief(user_id, prepared_prompt, wide_research)
        session = Session(
            agent_id=agent.id,
            user_id=user_id,
            memory_brief=memory_brief,
            goal=prepared_prompt.strip() or None,
            estimated_cost=estimated_cost,
            spent_credits=estimated_cost,
            max_budget=resolved_budget,
            mode=(mode or "auto").lower(),
            permissions=(permissions or "standard").lower(),
            risk_level=self._estimate_risk_level(prompt),
            model_tier=(model_tier or "lite").lower(),
            wide_research=wide_research,
        )
        logger.info(f"Created new Session with ID: {session.id} for user: {user_id}")
        await self._session_repository.save(session)
        return session

    async def _build_memory_brief(self, user_id: str, prompt: str = "", wide_research: bool = False) -> Optional[str]:
        summaries = await self._session_repository.find_summaries_by_user_id(user_id)
        recent = [s for s in summaries if s.latest_message][:5]
        lines = ["Use this as persistent cross-chat memory for Forge:"]
        for session in recent:
            title = session.title or "Untitled task"
            message = (session.latest_message or "").strip()
            if len(message) > 180:
                message = message[:177] + "..."
            lines.append(f"- {title}: {message}")
        if wide_research:
            lines.append("Wide research mode is enabled. Break the task into 5-8 subtopics, search each one, cross-check claims, and produce a structured report with citations and a summary.")
        if prompt.strip():
            lines.append(f"Current task goal: {prompt.strip()}")
        if len(lines) == 1:
            return None
        return "\n".join(lines)

    def _prepare_prompt(self, prompt: str, wide_research: bool) -> str:
        clean_prompt = (prompt or "").strip()
        if not wide_research:
            return clean_prompt
        return (
            "Use Wide Research mode for this task. Break the topic into 5-8 subtopics, research each subtopic separately, "
            "cross-reference findings, and produce a comprehensive report with citations, key takeaways, and next steps.\n\n"
            f"Research topic: {clean_prompt}"
        ).strip()

    def _estimate_cost(self, model_tier: str, message: str, wide_research: bool = False) -> int:
        tier = (model_tier or "lite").lower()
        base_cost_map = {"lite": 1, "regular": 2, "max": 6}
        base_cost = base_cost_map.get(tier, 2)
        task_cost = min(18, max(0, len((message or "").strip()) // 250))
        research_cost = 4 if wide_research else 0
        return base_cost + task_cost + research_cost

    def _estimate_risk_level(self, prompt: str) -> str:
        text = (prompt or "").lower()
        high_risk_terms = ("deploy", "production", "billing", "payment", "delete", "domain", "dns", "stripe", "netlify", "oauth")
        medium_risk_terms = ("login", "auth", "search", "research", "code", "file", "browser")
        if any(term in text for term in high_risk_terms):
            return "high"
        if any(term in text for term in medium_risk_terms):
            return "medium"
        return "low"

    async def _charge_credits(self, user_id: str, estimated_cost: int) -> None:
        await self._user_repository.add_credits(user_id, -estimated_cost)

    async def _create_agent(self, model_tier: str = "lite") -> Agent:
        logger.info("Creating new agent")
        settings = get_settings()
        tier = (model_tier or settings.model_tier or "lite").lower()
        if tier == "max":
            model_name = settings.model_name_max
            temperature = settings.temperature_max
            max_tokens = settings.max_tokens_max
        elif tier == "regular":
            model_name = settings.model_name_regular
            temperature = settings.temperature
            max_tokens = settings.max_tokens
        else:
            model_name = settings.model_name_lite
            temperature = settings.temperature_lite
            max_tokens = settings.max_tokens_lite
        agent = Agent(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        logger.info(f"Created new Agent with ID: {agent.id}")
        
        # Save agent to repository
        await self._agent_repository.save(agent)
        logger.info(f"Saved agent {agent.id} to repository")
        
        logger.info(f"Agent created successfully with ID: {agent.id}")
        return agent

    async def chat(
        self,
        session_id: str,
        user_id: str,
        message: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None,
        attachments: Optional[List[dict]] = None
    ) -> AsyncGenerator[AgentEvent, None]:
        message_preview = (message or "")[:50] if message else ""
        logger.info(f"Starting chat with session {session_id}: {message_preview}...")
        # Directly use the domain service's chat method, which will check if the session exists
        async for event in self._agent_domain_service.chat(session_id, user_id, message, timestamp, event_id, attachments):
            logger.debug(f"Received event: {event}")
            yield event
        logger.info(f"Chat with session {session_id} completed")
    
    async def get_session(self, session_id: str, user_id: Optional[str] = None) -> Optional[Session]:
        """Get a session by ID, ensuring it belongs to the user"""
        logger.info(f"Getting session {session_id} for user {user_id}")
        if not user_id:
            session = await self._session_repository.find_by_id(session_id)
        else:
            session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            logger.error(f"Session {session_id} not found for user {user_id}")
        return session
    
    async def get_all_sessions(self, user_id: str) -> List[SessionSummary]:
        """Get all sessions for a specific user (lightweight summaries)"""
        logger.info(f"Getting all sessions for user {user_id}")
        return await self._session_repository.find_summaries_by_user_id(user_id)

    async def delete_session(self, session_id: str, user_id: str) -> None:
        """Delete a session, ensuring it belongs to the user"""
        logger.info(f"Deleting session {session_id} for user {user_id}")
        # First verify the session belongs to the user
        session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            logger.error(f"Session {session_id} not found for user {user_id}")
            raise RuntimeError("Session not found")
        if session.sandbox_id:
            sandbox = await self._sandbox_cls.get(session.sandbox_id)
            if sandbox:
                await sandbox.destroy()
        
        await self._session_repository.delete(session_id)
        logger.info(f"Session {session_id} deleted successfully")

    async def stop_session(self, session_id: str, user_id: str) -> None:
        """Stop a session, ensuring it belongs to the user"""
        logger.info(f"Stopping session {session_id} for user {user_id}")
        # First verify the session belongs to the user
        session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            logger.error(f"Session {session_id} not found for user {user_id}")
            raise RuntimeError("Session not found")
        await self._agent_domain_service.stop_session(session_id)
        if session.sandbox_id:
            sandbox = await self._sandbox_cls.get(session.sandbox_id)
            if sandbox:
                await sandbox.destroy()
        logger.info(f"Session {session_id} stopped successfully")

    async def clear_unread_message_count(self, session_id: str, user_id: str) -> None:
        """Clear the unread message count for a session, ensuring it belongs to the user"""
        logger.info(f"Clearing unread message count for session {session_id} for user {user_id}")
        await self._session_repository.update_unread_message_count(session_id, 0)
        logger.info(f"Unread message count cleared for session {session_id}")

    async def get_session_followups(self, session_id: str, user_id: str) -> List[str]:
        session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            raise RuntimeError("Session not found")
        base = session.title or session.goal or "this task"
        if session.wide_research:
            return [
                f"Summarize the strongest findings from {base}",
                f"Turn {base} into a comparison spreadsheet",
                f"Create slides from {base}",
                f"Give me the next recommended actions based on {base}",
            ]
        return [
            f"Summarize {base} for me",
            f"Turn {base} into a spreadsheet",
            f"Create slides from {base}",
            f"Help me improve the result for {base}",
        ]

    async def update_session_title(self, session_id: str, user_id: str, title: str) -> None:
        """Rename a session, ensuring it belongs to the user"""
        session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            logger.error(f"Session {session_id} not found for user {user_id}")
            raise RuntimeError("Session not found")
        await self._session_repository.update_title(session_id, title.strip())
        logger.info(f"Session {session_id} renamed successfully")

    async def shutdown(self):
        logger.info("Closing all agents and cleaning up resources")
        # Clean up all Agents and their associated sandboxes
        await self._agent_domain_service.shutdown()
        logger.info("All agents closed successfully")

    async def shell_view(self, session_id: str, shell_session_id: str, user_id: str) -> ShellViewResponse:
        """View shell session output, ensuring session belongs to the user"""
        logger.info(f"Getting shell view for session {session_id} for user {user_id}")
        session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            logger.error(f"Session {session_id} not found for user {user_id}")
            raise RuntimeError("Session not found")
        
        if not session.sandbox_id:
            raise RuntimeError("Session has no sandbox environment")
        
        # Get sandbox and shell output
        sandbox = await self._sandbox_cls.get(session.sandbox_id)
        if not sandbox:
            raise RuntimeError("Sandbox environment not found")
        
        result = await sandbox.view_shell(shell_session_id, console=True)
        if result.success:
            return ShellViewResponse(**result.data)
        else:
            raise RuntimeError(f"Failed to get shell output: {result.message}")

    async def get_vnc_url(self, session_id: str) -> str:
        """Get VNC URL for a session, ensuring it belongs to the user"""
        logger.info(f"Getting VNC URL for session {session_id}")
        
        session = await self._session_repository.find_by_id(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            raise RuntimeError("Session not found")
        
        if not session.sandbox_id:
            raise RuntimeError("Session has no sandbox environment")
        
        # Get sandbox and return VNC URL
        sandbox = await self._sandbox_cls.get(session.sandbox_id)
        if not sandbox:
            raise RuntimeError("Sandbox environment not found")
        
        return sandbox.vnc_url

    async def file_view(self, session_id: str, file_path: str, user_id: str) -> FileViewResponse:
        """View file content, ensuring session belongs to the user"""
        logger.info(f"Getting file view for session {session_id} for user {user_id}")
        session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            logger.error(f"Session {session_id} not found for user {user_id}")
            raise RuntimeError("Session not found")
        
        if not session.sandbox_id:
            raise RuntimeError("Session has no sandbox environment")
        
        # Get sandbox and file content
        sandbox = await self._sandbox_cls.get(session.sandbox_id)
        if not sandbox:
            raise RuntimeError("Sandbox environment not found")
        
        result = await sandbox.file_read(file_path)
        if result.success:
            return FileViewResponse(**result.data)
        else:
            raise RuntimeError(f"Failed to read file: {result.message}")
    
    async def is_session_shared(self, session_id: str) -> bool:
        """Check if a session is shared"""
        logger.info(f"Checking if session {session_id} is shared")
        session = await self._session_repository.find_by_id(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            raise RuntimeError("Session not found")
        return session.is_shared

    async def get_session_files(self, session_id: str, user_id: Optional[str] = None) -> List[FileInfo]:
        """Get files for a session, ensuring it belongs to the user"""
        logger.info(f"Getting files for session {session_id} for user {user_id}")
        session = await self.get_session(session_id, user_id)
        return session.files
    
    async def get_shared_session_files(self, session_id: str) -> List[FileInfo]:
        """Get files for a shared session"""
        logger.info(f"Getting files for shared session {session_id}")
        session = await self._session_repository.find_by_id(session_id)
        if not session or not session.is_shared:
            logger.error(f"Shared session {session_id} not found or not shared")
            raise RuntimeError("Session not found")
        return session.files

    async def share_session(self, session_id: str, user_id: str) -> None:
        """Share a session, ensuring it belongs to the user"""
        logger.info(f"Sharing session {session_id} for user {user_id}")
        # First verify the session belongs to the user
        session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            logger.error(f"Session {session_id} not found for user {user_id}")
            raise RuntimeError("Session not found")
        
        await self._session_repository.update_shared_status(session_id, True)
        logger.info(f"Session {session_id} shared successfully")

    async def unshare_session(self, session_id: str, user_id: str) -> None:
        """Unshare a session, ensuring it belongs to the user"""
        logger.info(f"Unsharing session {session_id} for user {user_id}")
        # First verify the session belongs to the user
        session = await self._session_repository.find_by_id_and_user_id(session_id, user_id)
        if not session:
            logger.error(f"Session {session_id} not found for user {user_id}")
            raise RuntimeError("Session not found")
        
        await self._session_repository.update_shared_status(session_id, False)
        logger.info(f"Session {session_id} unshared successfully")

    async def get_shared_session(self, session_id: str) -> Optional[Session]:
        """Get a shared session by ID (no user authentication required)"""
        logger.info(f"Getting shared session {session_id}")
        session = await self._session_repository.find_by_id(session_id)
        if not session or not session.is_shared:
            logger.error(f"Shared session {session_id} not found or not shared")
            return None
        return session
