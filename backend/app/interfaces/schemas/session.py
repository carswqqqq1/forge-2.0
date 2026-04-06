from pydantic import BaseModel, field_validator
from typing import Optional, List
from app.interfaces.schemas.event import AgentSSEEvent
from app.domain.models.session import SessionStatus


class ChatRequest(BaseModel):
    """Chat request schema"""
    timestamp: Optional[int] = None
    message: Optional[str] = None
    attachments: Optional[List[dict]] = None
    event_id: Optional[str] = None


class CreateSessionRequest(BaseModel):
    """Create session request schema"""
    workspace_id: Optional[str] = None
    preset_id: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    instructions: Optional[str] = None

    @field_validator("workspace_id", "preset_id", "model_provider", "model_name", "instructions")
    @classmethod
    def validate_optional_text(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        value = v.strip()
        return value or None

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return None
        if v <= 0:
            raise ValueError("Max tokens must be positive")
        return v


class ShellViewRequest(BaseModel):
    """Shell view request schema"""
    session_id: str


class CreateSessionResponse(BaseModel):
    """Create session response schema"""
    session_id: str


class GetSessionResponse(BaseModel):
    """Get session response schema"""
    session_id: str
    title: Optional[str] = None
    workspace_id: Optional[str] = None
    status: SessionStatus
    events: List[AgentSSEEvent] = []
    is_shared: bool = False


class ListSessionItem(BaseModel):
    """List session item schema"""
    session_id: str
    title: Optional[str] = None
    workspace_id: Optional[str] = None
    latest_message: Optional[str] = None
    latest_message_at: Optional[int] = None
    status: SessionStatus
    unread_message_count: int
    is_shared: bool = False


class ListSessionResponse(BaseModel):
    """List session response schema"""
    sessions: List[ListSessionItem]


class ConsoleRecord(BaseModel):
    """Console record schema"""
    ps1: str
    command: str
    output: str


class ShellViewResponse(BaseModel):
    """Shell view response schema"""
    output: str
    session_id: str
    console: Optional[List[ConsoleRecord]] = None


class ShareSessionResponse(BaseModel):
    """Share session response schema"""
    session_id: str
    is_shared: bool


class SharedSessionResponse(BaseModel):
    """Shared session response schema (for public access)"""
    session_id: str
    title: Optional[str] = None
    status: SessionStatus
    events: List[AgentSSEEvent] = []
    is_shared: bool
