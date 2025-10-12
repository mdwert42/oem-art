"""
Tests for authentication utility functions.

Tests password hashing, verification, and JWT token operations.
"""

import pytest
from datetime import timedelta, datetime
from jose import jwt

from app.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.auth.config import AuthConfig
from app.schemas.auth import TokenData


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password(self):
        """Test that password hashing works and produces different hashes."""
        password = "test_password_123"
        hashed = hash_password(password)

        # Hash should be different from original password
        assert hashed != password

        # Hash should not be empty
        assert len(hashed) > 0

        # Hashing the same password twice should produce different results
        # (bcrypt adds a random salt)
        hashed2 = hash_password(password)
        assert hashed != hashed2

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "correct_password"
        hashed = hash_password(password)

        # Verification should succeed
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(correct_password)

        # Verification should fail
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword"
        hashed = hash_password(password)

        # Different case should fail
        assert verify_password("testpassword", hashed) is False
        assert verify_password("TESTPASSWORD", hashed) is False


class TestJWTTokenCreation:
    """Tests for JWT token creation."""

    def test_create_access_token_basic(self):
        """Test basic JWT token creation."""
        data = {"sub": "testuser", "user_id": 1, "role": "public"}
        token = create_access_token(data)

        # Token should not be empty
        assert token is not None
        assert len(token) > 0

        # Token should be a string
        assert isinstance(token, str)

        # Token should have three parts (header.payload.signature)
        assert token.count('.') == 2

    def test_create_access_token_with_expiration(self):
        """Test JWT token creation with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires_delta)

        # Decode token to check expiration
        payload = jwt.decode(
            token,
            AuthConfig.SECRET_KEY,
            algorithms=[AuthConfig.ALGORITHM]
        )

        # Check that expiration is set
        assert "exp" in payload

        # Expiration should be approximately 15 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (exp_time - now).total_seconds()

        # Allow 5 second tolerance
        assert 14 * 60 < time_diff < 16 * 60

    def test_create_access_token_includes_user_data(self):
        """Test that JWT token includes all user data."""
        data = {
            "sub": "testuser",
            "user_id": 42,
            "role": "admin"
        }
        token = create_access_token(data)

        # Decode token
        payload = jwt.decode(
            token,
            AuthConfig.SECRET_KEY,
            algorithms=[AuthConfig.ALGORITHM]
        )

        # Check that all data is included
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == 42
        assert payload["role"] == "admin"
        assert "exp" in payload


class TestJWTTokenDecoding:
    """Tests for JWT token decoding and validation."""

    def test_decode_valid_token(self):
        """Test decoding a valid JWT token."""
        # Create a token
        data = {
            "sub": "testuser",
            "user_id": 1,
            "role": "public"
        }
        token = create_access_token(data)

        # Decode the token
        token_data = decode_access_token(token)

        # Verify token data
        assert token_data is not None
        assert isinstance(token_data, TokenData)
        assert token_data.username == "testuser"
        assert token_data.user_id == 1
        assert token_data.role == "public"

    def test_decode_invalid_token(self):
        """Test decoding an invalid JWT token."""
        invalid_token = "this.is.not.a.valid.token"

        # Decoding should return None
        token_data = decode_access_token(invalid_token)
        assert token_data is None

    def test_decode_expired_token(self):
        """Test decoding an expired JWT token."""
        # Create a token that expires immediately
        data = {"sub": "testuser", "user_id": 1, "role": "public"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        # Decoding should return None for expired token
        token_data = decode_access_token(token)
        assert token_data is None

    def test_decode_token_with_wrong_secret(self):
        """Test that token with wrong secret fails validation."""
        # Create a token with a different secret
        data = {"sub": "testuser", "user_id": 1, "role": "public"}
        fake_token = jwt.encode(
            {**data, "exp": datetime.utcnow() + timedelta(minutes=30)},
            "wrong_secret_key",
            algorithm=AuthConfig.ALGORITHM
        )

        # Decoding should return None
        token_data = decode_access_token(fake_token)
        assert token_data is None

    def test_decode_token_missing_username(self):
        """Test decoding token without username (sub) field."""
        # Create token without 'sub' field
        data = {"user_id": 1, "role": "public"}
        # Manually create the token
        token = jwt.encode(
            {**data, "exp": datetime.utcnow() + timedelta(minutes=30)},
            AuthConfig.SECRET_KEY,
            algorithm=AuthConfig.ALGORITHM
        )

        # Decoding should return None
        token_data = decode_access_token(token)
        assert token_data is None

    def test_decode_token_with_partial_data(self):
        """Test decoding token with only username."""
        # Create token with minimal data
        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Decoding should still work
        token_data = decode_access_token(token)
        assert token_data is not None
        assert token_data.username == "testuser"
        # user_id and role should be None
        assert token_data.user_id is None
        assert token_data.role is None
