from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models.user import User
from ..schemas.auth import Token, LoginRequest
from ..schemas.user import UserResponse
from ..auth.utils import verify_password, create_access_token
from ..auth.dependencies import get_current_active_user
from ..auth.config import AuthConfig

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login endpoint.

    This endpoint accepts form data with username and password,
    and returns a JWT access token if authentication is successful.

    Args:
        form_data: OAuth2 form with username and password
        db: Database session

    Returns:
        Token object with access_token and token_type

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.

    This endpoint returns the user object for the currently authenticated user.
    Requires a valid JWT token in the Authorization header.

    Args:
        current_user: Authenticated user from dependency

    Returns:
        UserResponse object with user information
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout endpoint (placeholder).

    Since we're using stateless JWT tokens, logout is handled client-side
    by discarding the token. This endpoint is here for API completeness
    and could be extended with token blacklisting if needed.

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
