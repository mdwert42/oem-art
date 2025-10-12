"""
Shared pytest fixtures for all test suites.

This module provides common fixtures used across different test modules:
- Test database setup with SQLite in-memory
- Test client for API endpoint testing
- Sample user fixtures (admin, public, inactive)
- Authentication helpers
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator, Dict

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.auth.utils import hash_password, create_access_token


# Test database URL - using SQLite in-memory for fast tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """
    Create a test database engine.
    Uses SQLite in-memory database for fast, isolated tests.

    Scope: function - each test gets a fresh database
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """
    Create a test database session.

    This fixture provides a database session that is rolled back
    after each test to ensure test isolation.

    Scope: function - each test gets a fresh session
    """
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI test client with test database.

    This fixture overrides the get_db dependency to use the test database
    instead of the production database.

    Scope: function - each test gets a fresh client
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# User Fixtures

@pytest.fixture(scope="function")
def admin_user(test_db: Session) -> User:
    """
    Create an admin user for testing.

    Returns:
        User object with admin role
    """
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("admin_password"),
        role=UserRole.ADMIN,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def public_user(test_db: Session) -> User:
    """
    Create a public user for testing.

    Returns:
        User object with public role
    """
    user = User(
        username="public_user",
        email="public@test.com",
        hashed_password=hash_password("public_password"),
        role=UserRole.PUBLIC,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def inactive_user(test_db: Session) -> User:
    """
    Create an inactive user for testing.

    Returns:
        User object that is inactive
    """
    user = User(
        username="inactive_user",
        email="inactive@test.com",
        hashed_password=hash_password("inactive_password"),
        role=UserRole.PUBLIC,
        is_active=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


# Authentication Helpers

def get_auth_headers(user: User) -> Dict[str, str]:
    """
    Helper function to generate authentication headers for a user.

    Args:
        user: User object to generate token for

    Returns:
        Dictionary with Authorization header
    """
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        }
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def admin_auth_headers(admin_user: User) -> Dict[str, str]:
    """
    Get authentication headers for admin user.

    Returns:
        Dictionary with Authorization header for admin
    """
    return get_auth_headers(admin_user)


@pytest.fixture(scope="function")
def public_auth_headers(public_user: User) -> Dict[str, str]:
    """
    Get authentication headers for public user.

    Returns:
        Dictionary with Authorization header for public user
    """
    return get_auth_headers(public_user)
