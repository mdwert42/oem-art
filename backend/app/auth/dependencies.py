from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.auth import TokenData
from .utils import decode_access_token

# OAuth2 scheme for token extraction
# tokenUrl should point to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get the current authenticated user from JWT token.

    Args:
        token: JWT token extracted from Authorization header
        db: Database session

    Returns:
        User object if authentication is successful

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the token
    token_data: Optional[TokenData] = decode_access_token(token)

    if token_data is None or token_data.username is None:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.username == token_data.username).first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    FastAPI dependency to get current active user.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User object if user is active

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    FastAPI dependency to require admin role.
    Use this to protect admin-only endpoints.

    Args:
        current_user: User from get_current_active_user dependency

    Returns:
        User object if user is an admin

    Raises:
        HTTPException: If user is not an admin

    Example:
        @router.post("/admin/settings")
        async def update_settings(user: User = Depends(require_admin)):
            # Only admins can access this endpoint
            ...
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user
