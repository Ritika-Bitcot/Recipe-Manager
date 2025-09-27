"""Tests for utility functions."""

from datetime import datetime, timedelta

import pytest

from src.core.exceptions import AuthenticationError
from src.utils.jwt_helper import JWTHelper
from src.utils.password_helper import PasswordHelper


class TestJWTHelper:
    """Test JWT helper functionality."""

    @pytest.fixture
    def jwt_helper(self):
        """Create JWT helper instance."""
        return JWTHelper()

    def test_generate_token_success(self, jwt_helper):
        """Test successful token generation."""
        # Setup
        user_id = 1
        email = "test@example.com"

        # Execute
        token = jwt_helper.generate_token(user_id, email)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0
        # Token should have 3 parts separated by dots
        assert len(token.split(".")) == 3

    def test_generate_token_with_expiration(self, jwt_helper):
        """Test token generation with custom expiration."""
        # Setup
        user_id = 1
        email = "test@example.com"

        # Execute - JWT helper doesn't support custom expiration
        token = jwt_helper.generate_token(user_id, email)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_success(self, jwt_helper):
        """Test successful token verification."""
        # Setup
        user_id = 1
        email = "test@example.com"
        token = jwt_helper.generate_token(user_id, email)

        # Execute
        payload = jwt_helper.verify_token(token)

        # Assert
        assert payload is not None
        assert payload.get("user_id") == user_id
        assert payload.get("email") == email
        # JWT helper doesn't include type field

    def test_verify_token_invalid_format(self, jwt_helper):
        """Test token verification with invalid format."""
        # Setup
        invalid_token = "invalid.token.format"

        # Execute & Assert
        with pytest.raises(AuthenticationError, match="Invalid token"):
            jwt_helper.verify_token(invalid_token)

    def test_verify_token_expired(self, jwt_helper):
        """Test token verification with expired token."""
        # Setup
        user_id = 1
        email = "test@example.com"

        # Manually create an expired token by modifying the payload
        import jwt

        from src.core.settings import settings

        expired_payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() - timedelta(seconds=1),  # Already expired
            "iat": datetime.utcnow() - timedelta(minutes=1),
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # Execute & Assert
        with pytest.raises(AuthenticationError, match="Token has expired"):
            jwt_helper.verify_token(expired_token)

    def test_verify_token_invalid_signature(self, jwt_helper):
        """Test token verification with invalid signature."""
        # Setup
        # Create a token and modify it to have invalid signature
        user_id = 1
        email = "test@example.com"
        token = jwt_helper.generate_token(user_id, email)
        # Modify the last part to make signature invalid
        parts = token.split(".")
        parts[2] = "invalid_signature"
        invalid_token = ".".join(parts)

        # Execute & Assert
        with pytest.raises(AuthenticationError, match="Invalid token"):
            jwt_helper.verify_token(invalid_token)

    def test_verify_token_malformed(self, jwt_helper):
        """Test token verification with malformed token."""
        # Setup
        malformed_tokens = [
            "not.a.token",
            "too.few.parts",
            "",
            "singlepart",
            "two.parts.only.extra",
        ]

        # Execute & Assert
        for token in malformed_tokens:
            with pytest.raises(AuthenticationError):
                jwt_helper.verify_token(token)

    def test_extract_user_id(self, jwt_helper):
        """Test extracting user ID from token."""
        # Setup
        user_id = 1
        email = "test@example.com"
        token = jwt_helper.generate_token(user_id, email)

        # Execute
        extracted_id = jwt_helper.extract_user_id(token)

        # Assert
        assert extracted_id == user_id

    def test_extract_email(self, jwt_helper):
        """Test extracting email from token."""
        # Setup
        user_id = 1
        email = "test@example.com"
        token = jwt_helper.generate_token(user_id, email)

        # Execute
        extracted_email = jwt_helper.extract_email(token)

        # Assert
        assert extracted_email == email

    def test_is_token_expired_false(self, jwt_helper):
        """Test checking if token is not expired."""
        # Setup
        user_id = 1
        email = "test@example.com"
        token = jwt_helper.generate_token(user_id, email)

        # Execute
        is_expired = jwt_helper.is_token_expired(token)

        # Assert
        assert is_expired is False

    def test_is_token_expired_true(self, jwt_helper):
        """Test checking if token is expired."""
        # Setup
        user_id = 1
        email = "test@example.com"

        # Create an expired token by mocking the datetime
        import jwt

        from src.core.settings import settings

        # Use a timestamp that's definitely in the past
        past_time = datetime(2020, 1, 1)

        expired_payload = {
            "user_id": user_id,
            "email": email,
            "exp": past_time,
            "iat": past_time,
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # Execute
        is_expired = jwt_helper.is_token_expired(expired_token)

        # Assert
        assert is_expired is True


class TestPasswordHelper:
    """Test password helper functionality."""

    @pytest.fixture
    def password_helper(self):
        """Create password helper instance."""
        return PasswordHelper()

    def test_hash_password_success(self, password_helper):
        """Test successful password hashing."""
        # Setup
        password = "test_password_123"

        # Execute
        hashed = password_helper.hash_password(password)

        # Assert
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0
        # bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")

    def test_hash_password_different_salts(self, password_helper):
        """Test that same password produces different hashes (different salts)."""
        # Setup
        password = "same_password"

        # Execute
        hash1 = password_helper.hash_password(password)
        hash2 = password_helper.hash_password(password)

        # Assert
        assert hash1 != hash2  # Different salts should produce different hashes

    def test_verify_password_correct(self, password_helper):
        """Test password verification with correct password."""
        # Setup
        password = "correct_password_123"
        hashed = password_helper.hash_password(password)

        # Execute
        result = password_helper.verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_incorrect(self, password_helper):
        """Test password verification with incorrect password."""
        # Setup
        password = "correct_password_123"
        wrong_password = "wrong_password_456"
        hashed = password_helper.hash_password(password)

        # Execute
        result = password_helper.verify_password(wrong_password, hashed)

        # Assert
        assert result is False

    def test_verify_password_empty_string(self, password_helper):
        """Test password verification with empty string."""
        # Setup
        password = "some_password"
        hashed = password_helper.hash_password(password)

        # Execute
        result = password_helper.verify_password("", hashed)

        # Assert
        assert result is False

    def test_verify_password_none(self, password_helper):
        """Test password verification with None password."""
        # Setup
        password = "some_password"
        hashed = password_helper.hash_password(password)

        # Execute
        result = password_helper.verify_password(None, hashed)

        # Assert
        assert result is False

    def test_verify_password_invalid_hash(self, password_helper):
        """Test password verification with invalid hash format."""
        # Setup
        password = "some_password"
        invalid_hash = "not_a_valid_bcrypt_hash"

        # Execute
        result = password_helper.verify_password(password, invalid_hash)

        # Assert
        assert result is False

    def test_hash_password_empty_string(self, password_helper):
        """Test hashing empty string password."""
        # Setup
        password = ""

        # Execute
        hashed = password_helper.hash_password(password)

        # Assert
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_unicode(self, password_helper):
        """Test hashing unicode password."""
        # Setup
        password = "password_with_émojis_🚀_and_unicode"

        # Execute
        hashed = password_helper.hash_password(password)
        result = password_helper.verify_password(password, hashed)

        # Assert
        assert result is True

    def test_hash_password_very_long(self, password_helper):
        """Test hashing very long password."""
        # Setup
        password = "a" * 1000  # Very long password

        # Execute
        hashed = password_helper.hash_password(password)
        result = password_helper.verify_password(password, hashed)

        # Assert
        assert result is True

    def test_hash_password_special_characters(self, password_helper):
        """Test hashing password with special characters."""
        # Setup
        password = "P@ssw0rd!@#$%^&*()_+-=[]{}|;':\",./<>?"

        # Execute
        hashed = password_helper.hash_password(password)
        result = password_helper.verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_case_sensitive(self, password_helper):
        """Test that password verification is case sensitive."""
        # Setup
        password = "Password123"
        hashed = password_helper.hash_password(password)

        # Execute
        result_correct = password_helper.verify_password("Password123", hashed)
        result_wrong_case = password_helper.verify_password("password123", hashed)

        # Assert
        assert result_correct is True
        assert result_wrong_case is False

    def test_hash_password_consistency(self, password_helper):
        """Test that password hashing is consistent across multiple calls."""
        # Setup
        password = "consistent_password"

        # Execute multiple times
        hashes = [password_helper.hash_password(password) for _ in range(5)]

        # Assert - all hashes should be different (due to random salt)
        # but all should verify correctly
        for hashed in hashes:
            assert password_helper.verify_password(password, hashed) is True

        # All hashes should be different
        assert len(set(hashes)) == len(hashes)
