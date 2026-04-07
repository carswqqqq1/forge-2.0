from typing import Optional
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.domain.models.user import UserRole


class LoginRequest(BaseModel):
    """Login request schema"""
    email: str
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError("Valid email is required")
        return v.strip().lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class RegisterRequest(BaseModel):
    """Register request schema"""
    fullname: str
    email: str
    password: str
    
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
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    old_password: str
    new_password: str
    
    @field_validator('old_password')
    @classmethod
    def validate_old_password(cls, v):
        if not v:
            raise ValueError("Old password is required")
        return v
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError("New password must be at least 6 characters long")
        return v


class ChangeFullnameRequest(BaseModel):
    """Change fullname request schema"""
    fullname: str
    
    @field_validator('fullname')
    @classmethod
    def validate_fullname(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        return v.strip()


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str
    
    @field_validator('refresh_token')
    @classmethod
    def validate_refresh_token(cls, v):
        if not v:
            raise ValueError("Refresh token is required")
        return v


class SendVerificationCodeRequest(BaseModel):
    """Send verification code request schema"""
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError("Valid email is required")
        return v.strip().lower()


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    email: str
    verification_code: str
    new_password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError("Valid email is required")
        return v.strip().lower()
    
    @field_validator('verification_code')
    @classmethod
    def validate_verification_code(cls, v):
        if not v:
            raise ValueError("Verification code is required")
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Verification code must be 6 digits")
        return v
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError("New password must be at least 6 characters long")
        return v


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    fullname: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    credits: int = 0
    plan_name: str = "Forge Pro"
    plan_renewal_date: Optional[datetime] = None
    free_credits: int = 0
    monthly_credits: int = 0
    monthly_credits_max: int = 0
    daily_refresh_credits: int = 0
    preferred_language: str = "English"
    appearance: str = "light"
    receive_product_updates: bool = True
    email_when_queued_task_starts: bool = True
    nickname: str = ""
    occupation: str = ""
    more_about_you: str = ""
    custom_instructions: str = ""
    
    @staticmethod
    def from_user(user) -> 'UserResponse':
        """Convert user domain model to response schema"""
        return UserResponse(
            id=user.id,
            fullname=user.fullname,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            credits=getattr(user, "credits", 0),
            plan_name=getattr(user, "plan_name", "Forge Pro"),
            plan_renewal_date=getattr(user, "plan_renewal_date", None),
            free_credits=getattr(user, "free_credits", 0),
            monthly_credits=getattr(user, "monthly_credits", 0),
            monthly_credits_max=getattr(user, "monthly_credits_max", 0),
            daily_refresh_credits=getattr(user, "daily_refresh_credits", 0),
            preferred_language=getattr(user, "preferred_language", "English"),
            appearance=getattr(user, "appearance", "light"),
            receive_product_updates=getattr(user, "receive_product_updates", True),
            email_when_queued_task_starts=getattr(user, "email_when_queued_task_starts", True),
            nickname=getattr(user, "nickname", ""),
            occupation=getattr(user, "occupation", ""),
            more_about_you=getattr(user, "more_about_you", ""),
            custom_instructions=getattr(user, "custom_instructions", ""),
        )


class LoginResponse(BaseModel):
    """Login response schema"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Register response schema"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthStatusResponse(BaseModel):
    """Authentication status response schema"""
    auth_provider: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema"""
    access_token: str
    token_type: str = "bearer" 
