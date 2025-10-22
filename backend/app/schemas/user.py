from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Base user schema with common fields.

    Contains the fundamental user information shared across different user schemas.
    """
    username: str = Field(
        ...,
        description="Unique username for the user (3-50 characters)",
        examples=["admin", "john_doe", "artist123"],
        min_length=3,
        max_length=50
    )
    email: EmailStr = Field(
        ...,
        description="User's email address (must be unique and valid)",
        examples=["admin@art.oem", "john@example.com"]
    )


class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Used during user registration to create new user accounts.
    The password will be hashed before storage.
    """
    password: str = Field(
        ...,
        description="User's password (minimum 6 characters, will be hashed)",
        examples=["SecurePassword123!"],
        min_length=6
    )
    role: str = Field(
        default="public",
        description="User role - either 'admin' or 'public' (defaults to 'public')",
        examples=["public", "admin"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "john_doe",
                    "email": "john@example.com",
                    "password": "SecurePassword123!",
                    "role": "public"
                },
                {
                    "username": "admin",
                    "email": "admin@art.oem",
                    "password": "changeme",
                    "role": "admin"
                }
            ]
        }
    )


class UserUpdate(BaseModel):
    """
    Schema for updating user information.

    All fields are optional - only provided fields will be updated.
    Used by administrators to modify user accounts.
    """
    email: Optional[EmailStr] = Field(
        default=None,
        description="New email address for the user",
        examples=["newemail@example.com"]
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether the user account is active (can be used to disable accounts)",
        examples=[True, False]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "updated@example.com",
                    "is_active": True
                },
                {
                    "is_active": False
                }
            ]
        }
    )


class UserResponse(UserBase):
    """
    Schema for user responses (public-facing).

    Returned by API endpoints when retrieving user information.
    Does not include sensitive data like hashed passwords.

    Roles:
    - admin: Full access to all features (site owner)
    - public: Limited access (regular users)
    """
    id: int = Field(
        ...,
        description="Unique identifier for the user",
        examples=[1, 42]
    )
    role: str = Field(
        ...,
        description="User role - determines access level (admin or public)",
        examples=["admin", "public"]
    )
    is_active: bool = Field(
        ...,
        description="Whether the user account is active and can authenticate",
        examples=[True, False]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the user account was created",
        examples=["2025-01-15T10:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the user account was last updated",
        examples=["2025-01-20T14:45:00Z"]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "username": "admin",
                    "email": "admin@art.oem",
                    "id": 1,
                    "role": "admin",
                    "is_active": True,
                    "created_at": "2025-01-15T10:30:00Z",
                    "updated_at": "2025-01-15T10:30:00Z"
                },
                {
                    "username": "john_doe",
                    "email": "john@example.com",
                    "id": 42,
                    "role": "public",
                    "is_active": True,
                    "created_at": "2025-01-20T14:45:00Z",
                    "updated_at": "2025-01-20T14:45:00Z"
                }
            ]
        }
    )


class UserInDB(UserResponse):
    """
    Schema for user as stored in database (includes hashed password).

    Internal schema used for database operations. Should never be
    returned directly by API endpoints to avoid exposing password hashes.
    """
    hashed_password: str = Field(
        ...,
        description="Bcrypt hashed password (never exposed via API)",
        examples=["$2b$12$abcdefghijklmnopqrstuvwxyz0123456789"]
    )

    model_config = ConfigDict(from_attributes=True)
