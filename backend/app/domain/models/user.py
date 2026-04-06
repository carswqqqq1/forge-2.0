from typing import Optional, List
from datetime import datetime, UTC
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import uuid


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class ModelPreferences(BaseModel):
    """Default model configuration for new Forge sessions."""
    model_provider: str = "openai"
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000

    @field_validator("model_provider", "model_name")
    @classmethod
    def validate_required_text(cls, v: str) -> str:
        value = (v or "").strip()
        if not value:
            raise ValueError("Model provider and model name are required")
        return value

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Max tokens must be positive")
        return v


class UserMemoryItem(BaseModel):
    """A user-managed memory that should inform future sessions."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        value = (v or "").strip()
        if not value:
            raise ValueError("Memory content is required")
        return value


class Workspace(BaseModel):
    """Logical grouping for sessions and presets."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str
    description: str = ""
    color: str = "#0ea5e9"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        value = (v or "").strip()
        if not value:
            raise ValueError("Workspace name is required")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        return (v or "").strip()

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        value = (v or "").strip() or "#0ea5e9"
        if not value.startswith("#"):
            raise ValueError("Workspace color must be a hex value")
        return value


class AgentPreset(BaseModel):
    """Reusable session preset for Forge users."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str
    description: str = ""
    instructions: str = ""
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    workspace_id: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_preset_name(cls, v: str) -> str:
        value = (v or "").strip()
        if not value:
            raise ValueError("Preset name is required")
        return value

    @field_validator("description", "instructions")
    @classmethod
    def validate_free_text(cls, v: str) -> str:
        return (v or "").strip()

    @field_validator("model_provider", "model_name", "workspace_id")
    @classmethod
    def validate_optional_text(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        value = v.strip()
        return value or None

    @field_validator("temperature")
    @classmethod
    def validate_optional_temperature(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_optional_max_tokens(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return None
        if v <= 0:
            raise ValueError("Max tokens must be positive")
        return v


class ForgeProfile(BaseModel):
    """User-configurable Forge workspace state."""
    model_preferences: ModelPreferences = Field(default_factory=ModelPreferences)
    memories: List[UserMemoryItem] = Field(default_factory=list)
    workspaces: List[Workspace] = Field(default_factory=list)
    agent_presets: List[AgentPreset] = Field(default_factory=list)


class User(BaseModel):
    """User domain model"""
    id: str
    fullname: str
    email: str  # Now required field for login
    password_hash: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = datetime.now(UTC)
    updated_at: datetime = datetime.now(UTC)
    last_login_at: Optional[datetime] = None
    forge_profile: ForgeProfile = Field(default_factory=ForgeProfile)
    
    @field_validator('fullname')
    @classmethod
    def validate_fullname(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError("Valid email is required")
        return v.strip().lower()
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
    
    def deactivate(self):
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.now(UTC)
    
    def activate(self):
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.now(UTC) 
