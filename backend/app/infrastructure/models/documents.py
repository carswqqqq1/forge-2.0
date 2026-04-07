from typing import Dict, Optional, List, Type, TypeVar, Generic, get_args, Self, Any
from datetime import datetime, timezone, UTC
from beanie import Document
from pydantic import BaseModel, Field
from app.domain.models.agent import Agent
from app.domain.models.memory import Memory
from app.domain.models.event import AgentEvent
from app.domain.models.session import Session, SessionStatus
from app.domain.models.file import FileInfo
from app.domain.models.user import User, UserRole
from app.domain.models.claw import Claw, ClawStatus, ClawMessage
from pymongo import IndexModel, ASCENDING, DESCENDING

T = TypeVar('T', bound=BaseModel)

class BaseDocument(Document, Generic[T]):
    def __init_subclass__(cls, id_field="id", domain_model_class: Type[T] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._ID_FIELD = id_field
        cls._DOMAIN_MODEL_CLASS = domain_model_class
    
    def update_from_domain(self, domain_obj: T) -> None:
        """Update the document from domain model"""
        data = domain_obj.model_dump(exclude={'id', 'created_at'})
        data[self._ID_FIELD] = domain_obj.id
        if hasattr(self, 'updated_at'):
            data['updated_at'] = datetime.now(UTC)
        
        for field, value in data.items():
            setattr(self, field, value)
    
    def to_domain(self) -> T:
        """Convert MongoDB document to domain model"""
        # Convert to dict and map agent_id to id field
        data = self.model_dump(exclude={'id'})
        data['id'] = data.pop(self._ID_FIELD)
        return self._DOMAIN_MODEL_CLASS.model_validate(data)
    
    @classmethod
    def from_domain(cls, domain_obj: T) -> Self:
        """Create a new MongoDB agent from domain"""
        # Convert to dict and map id to agent_id field
        data = domain_obj.model_dump()
        data[cls._ID_FIELD] = data.pop('id')
        return cls.model_validate(data)

class UserDocument(BaseDocument[User], id_field="user_id", domain_model_class=User):
    """MongoDB document for User"""
    user_id: str
    fullname: str
    email: str  # Now required field for login
    password_hash: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    last_login_at: Optional[datetime] = None
    credits: int = 200
    plan_name: str = "Forge Pro"
    plan_renewal_date: Optional[datetime] = None
    free_credits: int = 0
    monthly_credits: int = 10000
    monthly_credits_max: int = 10000
    daily_refresh_credits: int = 100
    preferred_language: str = "English"
    appearance: str = "light"
    receive_product_updates: bool = True
    email_when_queued_task_starts: bool = True
    nickname: str = ""
    occupation: str = ""
    more_about_you: str = ""
    custom_instructions: str = ""

    class Settings:
        name = "users"
        indexes = [
            "user_id",
            "fullname",  # Keep fullname index but not unique
            IndexModel([("email", ASCENDING)], unique=True),  # Email as unique index
        ]

class AgentDocument(BaseDocument[Agent], id_field="agent_id", domain_model_class=Agent):
    """MongoDB document for Agent"""
    agent_id: str
    model_name: str
    temperature: float
    max_tokens: int
    memories: Dict[str, Memory] = {}
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "agents"
        indexes = [
            "agent_id",
        ]


class SessionDocument(BaseDocument[Session], id_field="session_id", domain_model_class=Session):
    """MongoDB model for Session"""
    session_id: str
    user_id: str  # User ID that owns this session
    sandbox_id: Optional[str] = None
    agent_id: str
    task_id: Optional[str] = None
    title: Optional[str] = None
    unread_message_count: int = 0
    latest_message: Optional[str] = None
    latest_message_at: Optional[datetime] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    events: List[AgentEvent]
    status: SessionStatus
    files: List[FileInfo] = []
    is_shared: Optional[bool] = False
    memory_brief: Optional[str] = None
    goal: Optional[str] = None
    estimated_cost: int = 0
    spent_credits: int = 0
    max_budget: int = 0
    mode: str = "auto"
    permissions: str = "standard"
    risk_level: str = "low"
    model_tier: str = "regular"
    wide_research: bool = False
    input_mode: str = "normal"
    mode_config: Dict[str, Any] = Field(default_factory=dict)
    class Settings:
        name = "sessions"
        indexes = [
            "session_id",
            "user_id",
            IndexModel(
                [("user_id", ASCENDING), ("latest_message_at", DESCENDING)],
                name="user_id_latest_message_at",
            ),
        ]


class ClawDocument(BaseDocument[Claw], id_field="claw_id", domain_model_class=Claw):
    """MongoDB document for Claw instance"""
    claw_id: str
    user_id: str
    container_name: Optional[str] = None
    container_ip: Optional[str] = None
    api_key: str
    status: ClawStatus = ClawStatus.CREATING
    error_message: Optional[str] = None
    expires_at: Optional[datetime] = None
    messages: List[ClawMessage] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "claws"
        indexes = [
            "claw_id",
            IndexModel([("user_id", ASCENDING)], unique=True),  # One claw per user
        ]


class UsageLedgerDocument(Document):
    ledger_id: str
    user_id: str
    source_type: str
    label: str
    credits_delta: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "usage_ledger"
        indexes = [
            "ledger_id",
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
        ]


class BillingActivityDocument(Document):
    activity_id: str
    user_id: str
    label: str
    amount: float = 0
    currency: str = "USD"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "billing_activity"
        indexes = [
            "activity_id",
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
        ]


class ScheduleDocument(Document):
    schedule_id: str
    user_id: str
    name: str
    description: str = ""
    schedule_text: str
    cron_expression: str
    next_run: Optional[datetime] = None
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "schedules"
        indexes = [
            "schedule_id",
            IndexModel([("user_id", ASCENDING), ("updated_at", DESCENDING)]),
        ]


class ConnectorDocument(Document):
    connection_id: str
    user_id: str
    connector_id: str
    name: str
    type: str = "app"
    auth_token: Optional[str] = None
    status: str = "connected"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    connected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "connectors"
        indexes = [
            "connection_id",
            IndexModel([("user_id", ASCENDING), ("connector_id", ASCENDING)], unique=True),
        ]


class ReferralDocument(Document):
    referral_id: str
    user_id: str
    referral_code: str
    invite_link: str
    credits_earned: int = 0
    referral_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "referrals"
        indexes = [
            "referral_id",
            IndexModel([("user_id", ASCENDING)], unique=True),
            IndexModel([("referral_code", ASCENDING)], unique=True),
        ]
