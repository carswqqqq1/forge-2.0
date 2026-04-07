from typing import Optional
from datetime import datetime, UTC
from pydantic import BaseModel, field_validator, EmailStr
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


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
