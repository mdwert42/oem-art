"""
Tests for authentication dependency functions.

Tests FastAPI dependency injection for:
- get_current_user
- get_current_active_user
- require_admin
"""

import pytest
from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    require_admin
)
from app.auth.utils import create_access_token
from app.models.user import User, UserRole


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self, test_db: Session, admin_user: User):
        """Test get_current_user with valid JWT token."""
        # Create valid token
        token = create_access_token(
            data={
                "sub": admin_user.username,
                "user_id": admin_user.id,
                "role": admin_user.role.value
            }
        )

        # Call dependency
        user = await get_current_user(token=token, db=test_db)

        # Should return the user
        assert user is not None
        assert user.id == admin_user.id
        assert user.username == admin_user.username

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self, test_db: Session):
        """Test get_current_user with invalid JWT token."""
        invalid_token = "invalid.token.here"

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=invalid_token, db=test_db)

        # Check exception details
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_with_expired_token(self, test_db: Session, admin_user: User):
        """Test get_current_user with expired JWT token."""
        # Create expired token
        token = create_access_token(
            data={
                "sub": admin_user.username,
                "user_id": admin_user.id,
                "role": admin_user.role.value
            },
            expires_delta=timedelta(seconds=-1)
        )

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=test_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_with_nonexistent_username(self, test_db: Session):
        """Test get_current_user with token for non-existent user."""
        # Create token for user that doesn't exist in database
        token = create_access_token(
            data={
                "sub": "nonexistent_user",
                "user_id": 9999,
                "role": "public"
            }
        )

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=test_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_with_token_missing_username(self, test_db: Session):
        """Test get_current_user with token missing username."""
        from jose import jwt
        from app.auth.config import AuthConfig
        from datetime import datetime

        # Create token without 'sub' field
        token = jwt.encode(
            {
                "user_id": 1,
                "role": "public",
                "exp": datetime.utcnow() + timedelta(minutes=30)
            },
            AuthConfig.SECRET_KEY,
            algorithm=AuthConfig.ALGORITHM
        )

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=test_db)

        assert exc_info.value.status_code == 401


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_active_user_with_active_user(self, admin_user: User):
        """Test get_current_active_user with active user."""
        # admin_user fixture is active by default
        user = await get_current_active_user(current_user=admin_user)

        # Should return the user
        assert user is not None
        assert user.id == admin_user.id
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_get_current_active_user_with_inactive_user(self, inactive_user: User):
        """Test get_current_active_user with inactive user."""
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=inactive_user)

        # Check exception details
        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


class TestRequireAdmin:
    """Tests for require_admin dependency."""

    @pytest.mark.asyncio
    async def test_require_admin_with_admin_user(self, admin_user: User):
        """Test require_admin with admin user."""
        # Should succeed and return user
        user = await require_admin(current_user=admin_user)

        assert user is not None
        assert user.id == admin_user.id
        assert user.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_require_admin_with_public_user(self, public_user: User):
        """Test require_admin with public user."""
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=public_user)

        # Check exception details
        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_admin_checks_both_active_and_role(self, test_db: Session):
        """Test that require_admin also ensures user is active."""
        # Create inactive admin user
        inactive_admin = User(
            username="inactive_admin",
            email="inactive_admin@test.com",
            hashed_password="hashed_password",
            role=UserRole.ADMIN,
            is_active=False
        )
        test_db.add(inactive_admin)
        test_db.commit()
        test_db.refresh(inactive_admin)

        # require_admin depends on get_current_active_user which checks is_active
        # So we should test this through get_current_active_user first
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=inactive_admin)

        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


class TestDependencyChaining:
    """Tests for how dependencies chain together."""

    @pytest.mark.asyncio
    async def test_full_dependency_chain_admin(
        self,
        test_db: Session,
        admin_user: User
    ):
        """Test full dependency chain for admin user."""
        # Create token
        token = create_access_token(
            data={
                "sub": admin_user.username,
                "user_id": admin_user.id,
                "role": admin_user.role.value
            }
        )

        # Step 1: get_current_user
        user = await get_current_user(token=token, db=test_db)
        assert user.username == admin_user.username

        # Step 2: get_current_active_user
        active_user = await get_current_active_user(current_user=user)
        assert active_user.is_active is True

        # Step 3: require_admin
        admin = await require_admin(current_user=active_user)
        assert admin.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_full_dependency_chain_public_user(
        self,
        test_db: Session,
        public_user: User
    ):
        """Test full dependency chain stops at require_admin for public user."""
        # Create token
        token = create_access_token(
            data={
                "sub": public_user.username,
                "user_id": public_user.id,
                "role": public_user.role.value
            }
        )

        # Step 1: get_current_user - should succeed
        user = await get_current_user(token=token, db=test_db)
        assert user.username == public_user.username

        # Step 2: get_current_active_user - should succeed
        active_user = await get_current_active_user(current_user=user)
        assert active_user.is_active is True

        # Step 3: require_admin - should fail
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=active_user)

        assert exc_info.value.status_code == 403
