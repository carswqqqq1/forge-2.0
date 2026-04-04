from datetime import UTC, datetime
from typing import List, Optional

from app.domain.models.event import BaseEvent
from app.domain.models.file import FileInfo
from app.domain.models.session import Session, SessionStatus, SessionSummary
from app.domain.repositories.session_repository import SessionRepository


class InMemorySessionRepository(SessionRepository):
    """In-memory session repository for standalone development."""

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def _clone(self, session: Session) -> Session:
        return session.model_copy(deep=True)

    def _require_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session

    async def save(self, session: Session) -> None:
        self._sessions[session.id] = self._clone(session)

    async def find_by_id(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        return self._clone(session) if session else None

    async def find_by_user_id(self, user_id: str) -> List[Session]:
        sessions = [session for session in self._sessions.values() if session.user_id == user_id]
        sessions.sort(key=lambda session: session.latest_message_at or session.created_at, reverse=True)
        return [self._clone(session) for session in sessions]

    async def find_summaries_by_user_id(self, user_id: str) -> List[SessionSummary]:
        sessions = await self.find_by_user_id(user_id)
        return [
            SessionSummary(
                id=session.id,
                user_id=session.user_id,
                title=session.title,
                workspace_id=session.workspace_id,
                unread_message_count=session.unread_message_count,
                latest_message=session.latest_message,
                latest_message_at=session.latest_message_at,
                status=session.status,
                is_shared=session.is_shared,
            )
            for session in sessions
        ]

    async def find_by_id_and_user_id(self, session_id: str, user_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session and session.user_id == user_id:
            return self._clone(session)
        return None

    async def update_title(self, session_id: str, title: str) -> None:
        session = self._require_session(session_id)
        session.title = title
        session.updated_at = datetime.now(UTC)

    async def update_latest_message(self, session_id: str, message: str, timestamp: datetime) -> None:
        session = self._require_session(session_id)
        session.latest_message = message
        session.latest_message_at = timestamp
        session.updated_at = datetime.now(UTC)

    async def add_event(self, session_id: str, event: BaseEvent) -> None:
        session = self._require_session(session_id)
        session.events.append(event.model_copy(deep=True))
        session.updated_at = datetime.now(UTC)

    async def add_file(self, session_id: str, file_info: FileInfo) -> None:
        session = self._require_session(session_id)
        session.files.append(file_info.model_copy(deep=True))
        session.updated_at = datetime.now(UTC)

    async def remove_file(self, session_id: str, file_id: str) -> None:
        session = self._require_session(session_id)
        session.files = [file for file in session.files if file.file_id != file_id]
        session.updated_at = datetime.now(UTC)

    async def get_file_by_path(self, session_id: str, file_path: str) -> Optional[FileInfo]:
        session = self._require_session(session_id)
        for file_info in session.files:
            if file_info.file_path == file_path:
                return file_info.model_copy(deep=True)
        return None

    async def update_status(self, session_id: str, status: SessionStatus) -> None:
        session = self._require_session(session_id)
        session.status = status
        session.updated_at = datetime.now(UTC)

    async def update_unread_message_count(self, session_id: str, count: int) -> None:
        session = self._require_session(session_id)
        session.unread_message_count = count
        session.updated_at = datetime.now(UTC)

    async def increment_unread_message_count(self, session_id: str) -> None:
        session = self._require_session(session_id)
        session.unread_message_count += 1
        session.updated_at = datetime.now(UTC)

    async def decrement_unread_message_count(self, session_id: str) -> None:
        session = self._require_session(session_id)
        session.unread_message_count = max(0, session.unread_message_count - 1)
        session.updated_at = datetime.now(UTC)

    async def update_shared_status(self, session_id: str, is_shared: bool) -> None:
        session = self._require_session(session_id)
        session.is_shared = is_shared
        session.updated_at = datetime.now(UTC)

    async def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    async def get_all(self) -> List[Session]:
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda session: session.latest_message_at or session.created_at, reverse=True)
        return [self._clone(session) for session in sessions]
