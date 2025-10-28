"""
Tests for authentication API endpoints.

Tests the /auth/* endpoints:
- POST /auth/login
- GET /auth/me
- POST /auth/logout
"""

import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestLoginEndpoint:
    """Tests for POST /auth/login endpoint."""

    def test_login_with_valid_credentials(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test login with valid username and password."""
        response = client.post(
            "/auth/login",
            data={
                "username": "admin",
                "password": "admin_password"
            }
        )

        # Should return 200 OK
        assert response.status_code == 200

        # Should return token
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_with_invalid_username(self, client: TestClient):
        """Test login with non-existent username."""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent",
                "password": "password"
            }
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Incorrect username or password" in data["detail"]

    def test_login_with_invalid_password(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test login with incorrect password."""
        response = client.post(
            "/auth/login",
            data={
                "username": "admin",
                "password": "wrong_password"
            }
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect username or password" in data["detail"]

    def test_login_with_inactive_user(
        self,
        client: TestClient,
        inactive_user: User
    ):
        """Test login with inactive user account."""
        response = client.post(
            "/auth/login",
            data={
                "username": "inactive_user",
                "password": "inactive_password"
            }
        )

        # Should return 400 Bad Request
        assert response.status_code == 400
        data = response.json()
        assert "Inactive user" in data["detail"]

    def test_login_missing_username(self, client: TestClient):
        """Test login without username."""
        response = client.post(
            "/auth/login",
            data={
                "password": "password"
            }
        )

        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == 422

    def test_login_missing_password(self, client: TestClient):
        """Test login without password."""
        response = client.post(
            "/auth/login",
            data={
                "username": "admin"
            }
        )

        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == 422

    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty username and password."""
        response = client.post(
            "/auth/login",
            data={
                "username": "",
                "password": ""
            }
        )

        # Should return 401 or 422
        assert response.status_code in [401, 422]

    def test_login_case_sensitive_username(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test that username is case-sensitive."""
        response = client.post(
            "/auth/login",
            data={
                "username": "ADMIN",  # uppercase
                "password": "admin_password"
            }
        )

        # Should fail because username is case-sensitive
        assert response.status_code == 401


class TestGetMeEndpoint:
    """Tests for GET /auth/me endpoint."""

    def test_get_me_with_valid_token(
        self,
        client: TestClient,
        admin_user: User,
        admin_auth_headers: dict
    ):
        """Test /auth/me with valid authentication token."""
        response = client.get(
            "/auth/me",
            headers=admin_auth_headers
        )

        # Should return 200 OK
        assert response.status_code == 200

        # Should return user data
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_me_with_public_user(
        self,
        client: TestClient,
        public_user: User,
        public_auth_headers: dict
    ):
        """Test /auth/me with public user token."""
        response = client.get(
            "/auth/me",
            headers=public_auth_headers
        )

        # Should return 200 OK
        assert response.status_code == 200

        # Should return public user data
        data = response.json()
        assert data["username"] == "public_user"
        assert data["role"] == "public"

    def test_get_me_with_invalid_token(self, client: TestClient):
        """Test /auth/me with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_me_with_malformed_header(self, client: TestClient):
        """Test /auth/me with malformed Authorization header."""
        # Missing "Bearer" prefix
        response = client.get(
            "/auth/me",
            headers={"Authorization": "some_token"}
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_me_does_not_return_password(
        self,
        client: TestClient,
        admin_user: User,
        admin_auth_headers: dict
    ):
        """Test that /auth/me does not return password hash."""
        response = client.get(
            "/auth/me",
            headers=admin_auth_headers
        )

        data = response.json()

        # Should not include password or hashed_password
        assert "password" not in data
        assert "hashed_password" not in data


class TestLogoutEndpoint:
    """Tests for POST /auth/logout endpoint."""

    def test_logout(self, client: TestClient):
        """Test logout endpoint."""
        response = client.post("/auth/logout")

        # Should return 200 OK
        assert response.status_code == 200

        # Should return success message
        data = response.json()
        assert "message" in data
        assert "logged out" in data["message"].lower()

    def test_logout_with_token(
        self,
        client: TestClient,
        admin_auth_headers: dict
    ):
        """Test logout with authentication token."""
        # Note: Our logout is stateless, so token is not required
        response = client.post(
            "/auth/logout",
            headers=admin_auth_headers
        )

        # Should still return 200 OK
        assert response.status_code == 200

    def test_logout_without_token(self, client: TestClient):
        """Test logout without authentication token."""
        # Should still work (stateless logout)
        response = client.post("/auth/logout")

        assert response.status_code == 200


class TestEndpointIntegration:
    """Integration tests across multiple endpoints."""

    def test_login_logout_then_access_me(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test that token still works after logout (stateless)."""
        # Step 1: Login
        login_response = client.post(
            "/auth/login",
            data={
                "username": "admin",
                "password": "admin_password"
            }
        )

        token = login_response.json()["access_token"]

        # Step 2: Logout
        logout_response = client.post("/auth/logout")
        assert logout_response.status_code == 200

        # Step 3: Try to access /auth/me with same token
        # Note: Since our logout is stateless, token should still work
        # (In production, you might implement token blacklisting)
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Token should still work (stateless JWT)
        assert me_response.status_code == 200
