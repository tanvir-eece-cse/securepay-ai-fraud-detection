"""
Pydantic Schemas for User Operations
Request and Response schemas for authentication and user management.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
import re


# ============== Base Schemas ==============

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^01[3-9]\d{8}$")  # Bangladesh phone format
    organization: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)


# ============== Registration Schemas ==============

class UserRegister(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=12)
    confirm_password: str = Field(..., min_length=12)
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Ensure passwords match."""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
    
    @validator("phone")
    def validate_bd_phone(cls, v):
        """Validate Bangladesh phone number format."""
        if v and not re.match(r"^01[3-9]\d{8}$", v):
            raise ValueError("Invalid Bangladesh phone number format")
        return v


class UserCreate(UserBase):
    """Schema for admin user creation."""
    password: str = Field(..., min_length=12)
    role: str = Field(default="viewer")
    is_active: bool = True


# ============== Login Schemas ==============

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str
    mfa_code: Optional[str] = Field(None, min_length=6, max_length=6)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    mfa_required: bool = False


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class MFASetupResponse(BaseModel):
    """Schema for MFA setup response."""
    secret: str
    qr_uri: str
    backup_codes: List[str]


class MFAVerifyRequest(BaseModel):
    """Schema for MFA verification request."""
    code: str = Field(..., min_length=6, max_length=6)


# ============== User Response Schemas ==============

class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    organization: Optional[str]
    department: Optional[str]
    job_title: Optional[str]
    role: str
    status: str
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Schema for user profile."""
    id: UUID
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str]
    organization: Optional[str]
    department: Optional[str]
    job_title: Optional[str]
    role: str
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for user profile update."""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    organization: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    
    @validator("phone")
    def validate_bd_phone(cls, v):
        if v and not re.match(r"^01[3-9]\d{8}$", v):
            raise ValueError("Invalid Bangladesh phone number format")
        return v


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=12)
    confirm_password: str
    
    @validator("new_password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=12)
    confirm_password: str


# ============== Admin Schemas ==============

class UserAdminUpdate(BaseModel):
    """Schema for admin user update."""
    role: Optional[str] = None
    status: Optional[str] = None
    is_superuser: Optional[bool] = None
    force_password_change: Optional[bool] = None


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== API Key Schemas ==============

class APIKeyCreate(BaseModel):
    """Schema for API key creation."""
    name: str = Field(..., min_length=3, max_length=100)
    scopes: Optional[List[str]] = None
    expires_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """Schema for API key response."""
    id: UUID
    name: str
    key_prefix: str
    scopes: Optional[List[str]]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class APIKeyCreated(APIKeyResponse):
    """Schema for newly created API key (includes full key)."""
    key: str  # Only returned once at creation
