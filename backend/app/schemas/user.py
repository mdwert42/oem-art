from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    role: str = "public"  # Default role is public


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user responses (public-facing)"""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schema for user as stored in database (includes hashed password)"""
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)
