from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class LoginRequest(BaseModel):
    """
    Request schema for user login.

    Used to authenticate users and obtain JWT access tokens.
    """
    username: str = Field(
        ...,
        description="The user's unique username",
        examples=["admin", "john_doe"],
        min_length=3,
        max_length=50
    )
    password: str = Field(
        ...,
        description="The user's password (will be verified against hashed password)",
        examples=["SecurePassword123!"],
        min_length=6
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "admin",
                    "password": "changeme"
                },
                {
                    "username": "john_doe",
                    "password": "MySecurePass123!"
                }
            ]
        }
    )


class Token(BaseModel):
    """
    Response schema for token endpoints.

    Contains the JWT access token and token type for Bearer authentication.
    This token should be included in the Authorization header for protected endpoints.
    """
    access_token: str = Field(
        ...,
        description="JWT access token to be used for authentication",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTY0MDAwMDAwMH0.signature"]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type - always 'bearer' for JWT tokens",
        examples=["bearer"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTY0MDAwMDAwMH0.signature",
                    "token_type": "bearer"
                }
            ]
        }
    )


class TokenData(BaseModel):
    """
    Data contained within the JWT token payload.

    This schema represents the claims embedded in the JWT token after decoding.
    These values are used internally for authentication and authorization.
    """
    username: Optional[str] = Field(
        default=None,
        description="The username of the authenticated user",
        examples=["admin", "john_doe"]
    )
    user_id: Optional[int] = Field(
        default=None,
        description="The unique identifier of the authenticated user",
        examples=[1, 42]
    )
    role: Optional[str] = Field(
        default=None,
        description="The role of the authenticated user (admin or public)",
        examples=["admin", "public"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "admin",
                    "user_id": 1,
                    "role": "admin"
                },
                {
                    "username": "john_doe",
                    "user_id": 42,
                    "role": "public"
                }
            ]
        }
    )


class RefreshTokenRequest(BaseModel):
    """
    Request schema for refreshing tokens (future implementation).

    Will be used to obtain a new access token using a refresh token.
    """
    refresh_token: str = Field(
        ...,
        description="The refresh token previously issued to the user",
        examples=["refresh_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )


class PasswordChangeRequest(BaseModel):
    """
    Request schema for changing password (future implementation).

    Allows authenticated users to change their password by providing
    their current password and a new password.
    """
    current_password: str = Field(
        ...,
        description="The user's current password for verification",
        examples=["OldPassword123!"],
        min_length=6
    )
    new_password: str = Field(
        ...,
        description="The new password to set (must meet security requirements)",
        examples=["NewSecurePassword456!"],
        min_length=6
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "current_password": "OldPassword123!",
                    "new_password": "NewSecurePassword456!"
                }
            ]
        }
    )
