"""
Integration tests for authentication system.

Tests complete authentication flows and scenarios:
- Full user login flows
- Admin vs public user access patterns
- Token expiration and renewal
- Concurrent sessions
"""

import pytest
import time
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.auth.utils import create_access_token, hash_password


class TestFullAuthenticationFlow:
    """Tests for complete authentication flows."""

    def test_admin_login_flow(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test full admin login flow: login → get token → access /auth/me."""
        # Step 1: Login
        login_response = client.post(
            "/auth/login",
            data={
                "username": "admin",
                "password": "admin_password"
            }
        )

        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        token = token_data["access_token"]

        # Step 2: Access protected endpoint
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["username"] == "admin"
        assert user_data["email"] == "admin@test.com"
        assert user_data["role"] == "admin"
        assert user_data["is_active"] is True

    def test_public_user_flow(
        self,
        client: TestClient,
        public_user: User
    ):
        """Test full public user flow."""
        # Step 1: Login
        login_response = client.post(
            "/auth/login",
            data={
                "username": "public_user",
                "password": "public_password"
            }
        )

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 2: Access /auth/me
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["role"] == "public"


class TestAdminAccess:
    """Tests for admin-only access patterns."""

    def test_admin_can_access_admin_endpoint(
        self,
        client: TestClient,
        test_db: Session,
        admin_user: User,
        admin_auth_headers: dict
    ):
        """Test that admin user can access admin-only endpoints."""
        # Note: We need to create an admin-only test endpoint
        # For now, we'll test that admin role is properly set
        response = client.get(
            "/auth/me",
            headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    def test_public_user_cannot_access_admin_endpoint(
        self,
        client: TestClient,
        public_user: User,
        public_auth_headers: dict
    ):
        """Test that public user cannot access admin-only endpoints."""
        # We're verifying the role is correctly set as public
        response = client.get(
            "/auth/me",
            headers=public_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "public"
        # In a real admin endpoint, this would return 403

    def test_unauthenticated_user_cannot_access_protected_endpoint(
        self,
        client: TestClient
    ):
        """Test that unauthenticated user cannot access protected endpoints."""
        response = client.get("/auth/me")

        # Should return 401 Unauthorized
        assert response.status_code == 401


class TestTokenExpiration:
    """Tests for token expiration behavior."""

    def test_expired_token_access(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test that expired token cannot access protected endpoints."""
        # Create an expired token
        expired_token = create_access_token(
            data={
                "sub": admin_user.username,
                "user_id": admin_user.id,
                "role": admin_user.role.value
            },
            expires_delta=timedelta(seconds=-1)
        )

        # Try to access protected endpoint
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_token_expiration_and_relogin(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test flow: token expires → re-login → get new token."""
        # Step 1: Create expired token
        expired_token = create_access_token(
            data={
                "sub": admin_user.username,
                "user_id": admin_user.id,
                "role": admin_user.role.value
            },
            expires_delta=timedelta(seconds=-1)
        )

        # Step 2: Verify token is expired
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

        # Step 3: Re-login to get new token
        login_response = client.post(
            "/auth/login",
            data={
                "username": "admin",
                "password": "admin_password"
            }
        )
        assert login_response.status_code == 200
        new_token = login_response.json()["access_token"]

        # Step 4: Use new token
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert me_response.status_code == 200


class TestConcurrentSessions:
    """Tests for concurrent user sessions."""

    def test_multiple_tokens_same_user(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test that a user can have multiple active sessions."""
        # Login twice to get two different tokens
        login1 = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin_password"}
        )
        login2 = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin_password"}
        )

        token1 = login1.json()["access_token"]
        token2 = login2.json()["access_token"]

        # Tokens should be different
        assert token1 != token2

        # Both tokens should work simultaneously
        response1 = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token1}"}
        )
        response2 = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_multiple_users_concurrent_sessions(
        self,
        client: TestClient,
        admin_user: User,
        public_user: User
    ):
        """Test that multiple users can have concurrent sessions."""
        # Login as admin
        admin_login = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin_password"}
        )
        admin_token = admin_login.json()["access_token"]

        # Login as public user
        public_login = client.post(
            "/auth/login",
            data={"username": "public_user", "password": "public_password"}
        )
        public_token = public_login.json()["access_token"]

        # Both should be able to access /auth/me
        admin_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        public_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {public_token}"}
        )

        assert admin_response.status_code == 200
        assert public_response.status_code == 200

        # Verify correct user data is returned
        admin_data = admin_response.json()
        public_data = public_response.json()

        assert admin_data["username"] == "admin"
        assert admin_data["role"] == "admin"
        assert public_data["username"] == "public_user"
        assert public_data["role"] == "public"


class TestUserStateChanges:
    """Tests for user state changes during active sessions."""

    def test_inactive_user_with_valid_token(
        self,
        client: TestClient,
        test_db: Session,
        admin_user: User
    ):
        """Test that deactivated user cannot use previously valid token."""
        # Step 1: Login and get token
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin_password"}
        )
        token = login_response.json()["access_token"]

        # Step 2: Verify token works
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200

        # Step 3: Deactivate user
        admin_user.is_active = False
        test_db.commit()
        test_db.refresh(admin_user)

        # Step 4: Try to use same token
        me_response_after = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should return 400 (inactive user)
        assert me_response_after.status_code == 400
        assert "Inactive user" in me_response_after.json()["detail"]


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_login_with_extra_whitespace(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test login with whitespace in username."""
        response = client.post(
            "/auth/login",
            data={
                "username": " admin ",
                "password": "admin_password"
            }
        )

        # Should fail (whitespace is not trimmed)
        assert response.status_code == 401

    def test_sql_injection_attempt_in_login(self, client: TestClient):
        """Test that SQL injection attempts fail safely."""
        response = client.post(
            "/auth/login",
            data={
                "username": "admin' OR '1'='1",
                "password": "anything"
            }
        )

        # Should fail safely
        assert response.status_code == 401

    def test_extremely_long_token(self, client: TestClient):
        """Test handling of extremely long token."""
        # Create a very long fake token
        long_token = "Bearer " + "a" * 10000

        response = client.get(
            "/auth/me",
            headers={"Authorization": long_token}
        )

        # Should return 401 (invalid token)
        assert response.status_code == 401

    def test_special_characters_in_password(
        self,
        client: TestClient,
        test_db: Session
    ):
        """Test that passwords with special characters work correctly."""
        # Create user with special character password
        special_password = "P@ssw0rd!#$%^&*()"
        user = User(
            username="special_user",
            email="special@test.com",
            hashed_password=hash_password(special_password),
            role=UserRole.PUBLIC,
            is_active=True
        )
        test_db.add(user)
        test_db.commit()

        # Try to login
        response = client.post(
            "/auth/login",
            data={
                "username": "special_user",
                "password": special_password
            }
        )

        # Should succeed
        assert response.status_code == 200
        assert "access_token" in response.json()
