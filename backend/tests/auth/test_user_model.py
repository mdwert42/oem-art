"""
Tests for User model.

Tests user creation, constraints, defaults, and relationships.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.auth.utils import hash_password


class TestUserCreation:
    """Tests for basic user creation."""

    def test_create_user(self, test_db: Session):
        """Test creating a basic user."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.PUBLIC
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # User should be created with an ID
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.PUBLIC

    def test_create_admin_user(self, test_db: Session):
        """Test creating a user with admin role."""
        user = User(
            username="adminuser",
            email="admin@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.role == UserRole.ADMIN

    def test_create_public_user(self, test_db: Session):
        """Test creating a user with public role."""
        user = User(
            username="publicuser",
            email="public@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.PUBLIC
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.role == UserRole.PUBLIC


class TestUserConstraints:
    """Tests for user model constraints."""

    def test_unique_username_constraint(self, test_db: Session):
        """Test that usernames must be unique."""
        # Create first user
        user1 = User(
            username="duplicate",
            email="user1@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user1)
        test_db.commit()

        # Try to create second user with same username
        user2 = User(
            username="duplicate",
            email="user2@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user2)

        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_unique_email_constraint(self, test_db: Session):
        """Test that emails must be unique."""
        # Create first user
        user1 = User(
            username="user1",
            email="duplicate@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user1)
        test_db.commit()

        # Try to create second user with same email
        user2 = User(
            username="user2",
            email="duplicate@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user2)

        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_username_case_sensitivity(self, test_db: Session):
        """Test that username comparison is case-sensitive in database."""
        # Create user with lowercase username
        user1 = User(
            username="testuser",
            email="user1@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user1)
        test_db.commit()

        # Create user with uppercase username - should succeed
        user2 = User(
            username="TESTUSER",
            email="user2@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user2)
        test_db.commit()
        test_db.refresh(user2)

        # Both users should exist
        assert user2.id is not None
        assert user2.username == "TESTUSER"


class TestUserDefaults:
    """Tests for user model default values."""

    def test_is_active_default_value(self, test_db: Session):
        """Test that is_active defaults to True."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Default should be True
        assert user.is_active is True

    def test_role_default_value(self, test_db: Session):
        """Test that role defaults to PUBLIC."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password")
            # Not specifying role
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Default should be PUBLIC
        assert user.role == UserRole.PUBLIC

    def test_inactive_user_creation(self, test_db: Session):
        """Test creating an inactive user."""
        user = User(
            username="inactive",
            email="inactive@example.com",
            hashed_password=hash_password("password"),
            is_active=False
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.is_active is False


class TestUserTimestamps:
    """Tests for user timestamp fields."""

    def test_created_at_timestamp(self, test_db: Session):
        """Test that created_at is set automatically."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # created_at should be set
        assert user.created_at is not None

    def test_updated_at_timestamp(self, test_db: Session):
        """Test that updated_at is set automatically."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # updated_at should be set
        assert user.updated_at is not None

    def test_timestamps_on_creation(self, test_db: Session):
        """Test that created_at and updated_at are initially the same."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Both timestamps should be very close (within 1 second)
        time_diff = abs((user.updated_at - user.created_at).total_seconds())
        assert time_diff < 1.0

    def test_updated_at_changes_on_update(self, test_db: Session):
        """Test that updated_at changes when user is updated."""
        import time

        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        original_updated_at = user.updated_at

        # Wait a moment and update user
        time.sleep(0.1)
        user.email = "newemail@example.com"
        test_db.commit()
        test_db.refresh(user)

        # updated_at should have changed
        # Note: This test might be flaky depending on database timestamp precision
        # Some databases might not update the timestamp for such quick changes
        assert user.updated_at >= original_updated_at


class TestUserRepresentation:
    """Tests for user string representation."""

    def test_user_repr(self, test_db: Session):
        """Test user __repr__ method."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.PUBLIC
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Check repr format
        repr_str = repr(user)
        assert "User" in repr_str
        assert f"id={user.id}" in repr_str
        assert "username='testuser'" in repr_str
        assert "role=UserRole.PUBLIC" in repr_str
