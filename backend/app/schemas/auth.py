from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Request schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """Response schema for token endpoints"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data contained within the JWT token"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing tokens"""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Request schema for changing password (future use)"""
    current_password: str
    new_password: str
