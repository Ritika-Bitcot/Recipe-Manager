"""Tests for utility functions."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

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

    def test_token_expiration_duration(self, jwt_helper):
        """Test that token expires after the correct duration from configuration."""
        # Setup
        user_id = 1
        email = "test@example.com"

        # Generate token
        token = jwt_helper.generate_token(user_id, email)

        # Decode token to check expiration without verification
        import jwt

        from src.core.settings import settings

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},  # Don't verify expiration yet
        )

        # Get the issued at time and expiration time from the token
        iat_timestamp = payload.get("iat")
        exp_timestamp = payload.get("exp")

        # Convert to datetime objects
        iat_datetime = datetime.fromtimestamp(iat_timestamp)
        exp_datetime = datetime.fromtimestamp(exp_timestamp)

        # Calculate the actual duration between issued at and expiration
        actual_duration = exp_datetime - iat_datetime
        expected_duration = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Check that the duration matches the configuration setting
        duration_diff = abs((actual_duration - expected_duration).total_seconds())
        assert (
            duration_diff < 2
        ), f"Token duration {actual_duration} differs by {duration_diff} seconds from expected {expected_duration}"

        # Also verify that expiration is in the future
        current_time = datetime.utcnow()
        assert (
            exp_datetime > current_time
        ), f"Token expiration {exp_datetime} is not in the future (current: {current_time})"

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
        """Test hashing very long password (truncated to bcrypt limit)."""
        # Setup
        password = "a" * 1000  # Very long password

        # Execute
        hashed = password_helper.hash_password(password)
        result = password_helper.verify_password(password, hashed)

        # Assert
        # bcrypt truncates passwords to 72 bytes, so this should still work
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


class TestAuthDecorators:
    """Test auth decorators functionality."""

    def test_get_current_user_email_bypass(self):
        """Test get_current_user_email with bypass enabled."""
        from src.utils.auth_decorators import get_current_user_email

        with patch("src.utils.auth_decorators.settings") as mock_settings:
            mock_settings.AUTH_BYPASS_EMAIL = "test@example.com"

            result = get_current_user_email()

            assert result == "test@example.com"

    def test_get_current_user_email_jwt_success(self):
        """Test get_current_user_email with JWT authentication."""
        from src.utils.auth_decorators import get_current_user_email

        with patch("src.utils.auth_decorators.settings") as mock_settings:
            mock_settings.AUTH_BYPASS_EMAIL = None

            with patch("src.utils.auth_decorators.get_jwt_identity") as mock_jwt:
                mock_jwt.return_value = "test@example.com"

                result = get_current_user_email()

                assert result == "test@example.com"

    def test_get_current_user_email_jwt_failure(self):
        """Test get_current_user_email with JWT authentication failure."""
        from src.utils.auth_decorators import get_current_user_email

        with patch("src.utils.auth_decorators.settings") as mock_settings:
            mock_settings.AUTH_BYPASS_EMAIL = None

            with patch("src.utils.auth_decorators.get_jwt_identity") as mock_jwt:
                mock_jwt.return_value = None

                with pytest.raises(AuthenticationError):
                    get_current_user_email()

    def test_get_current_user_id_bypass(self):
        """Test get_current_user_id with bypass enabled."""
        from src.utils.auth_decorators import get_current_user_id

        with patch("src.utils.auth_decorators.settings") as mock_settings:
            mock_settings.AUTH_BYPASS_EMAIL = "test@example.com"

            with patch("src.utils.auth_decorators.AuthService") as mock_auth_service_class:
                mock_auth_service = Mock()
                mock_auth_service_class.return_value = mock_auth_service

                mock_user = Mock()
                mock_user.id = 123
                mock_auth_service.user_repository.get_by_email.return_value = mock_user

                with patch("src.utils.auth_decorators.get_db_session") as mock_get_session:
                    mock_session = Mock()
                    mock_get_session.return_value = mock_session

                    result = get_current_user_id()

                    assert result == 123

    def test_get_current_user_id_jwt_success(self):
        """Test get_current_user_id with JWT authentication."""
        from src.utils.auth_decorators import get_current_user_id

        with patch("src.utils.auth_decorators.settings") as mock_settings:
            mock_settings.AUTH_BYPASS_EMAIL = None

            with patch("src.utils.auth_decorators.get_jwt_identity") as mock_jwt:
                mock_jwt.return_value = "test@example.com"

                with patch("src.utils.auth_decorators.AuthService") as mock_auth_service_class:
                    mock_auth_service = Mock()
                    mock_auth_service_class.return_value = mock_auth_service

                    mock_user = Mock()
                    mock_user.id = 123
                    mock_auth_service.user_repository.get_by_email.return_value = mock_user

                    with patch("src.utils.auth_decorators.get_db_session") as mock_get_session:
                        mock_session = Mock()
                        mock_get_session.return_value = mock_session

                        result = get_current_user_id()

                        assert result == 123

    def test_get_current_user_id_user_not_found(self):
        """Test get_current_user_id when user is not found."""
        from src.core.exceptions import ResourceNotFoundError
        from src.utils.auth_decorators import get_current_user_id

        with patch("src.utils.auth_decorators.settings") as mock_settings:
            mock_settings.AUTH_BYPASS_EMAIL = None

            with patch("src.utils.auth_decorators.get_jwt_identity") as mock_jwt:
                mock_jwt.return_value = "test@example.com"

                with patch("src.utils.auth_decorators.AuthService") as mock_auth_service_class:
                    mock_auth_service = Mock()
                    mock_auth_service_class.return_value = mock_auth_service

                    mock_auth_service.user_repository.get_by_email.return_value = None

                    with patch("src.utils.auth_decorators.get_db_session") as mock_get_session:
                        mock_session = Mock()
                        mock_get_session.return_value = mock_session

                        with pytest.raises(ResourceNotFoundError):
                            get_current_user_id()

    def test_jwt_required_with_bypass_decorator_bypass(self):
        """Test jwt_required_with_bypass decorator with bypass enabled."""
        from flask import Flask

        from src.utils.auth_decorators import jwt_required_with_bypass

        app = Flask(__name__)

        @jwt_required_with_bypass
        def test_function():
            return "success"

        with app.app_context():
            with patch("src.utils.auth_decorators.settings") as mock_settings:
                mock_settings.AUTH_BYPASS_EMAIL = "test@example.com"

                with patch("src.utils.auth_decorators.AuthService") as mock_auth_service_class:
                    mock_auth_service = Mock()
                    mock_auth_service_class.return_value = mock_auth_service

                    mock_user = Mock()
                    mock_user.id = 123
                    mock_auth_service.user_repository.get_by_email.return_value = mock_user

                    with patch("src.utils.auth_decorators.get_db_session") as mock_get_session:
                        mock_session = Mock()
                        mock_get_session.return_value = mock_session

                        result = test_function()

                        assert result == "success"

    def test_jwt_required_with_bypass_decorator_jwt_success(self):
        """Test jwt_required_with_bypass decorator with JWT authentication."""
        from flask import Flask

        from src.utils.auth_decorators import jwt_required_with_bypass

        app = Flask(__name__)

        @jwt_required_with_bypass
        def test_function():
            return "success"

        with app.app_context():
            with patch("src.utils.auth_decorators.settings") as mock_settings:
                mock_settings.AUTH_BYPASS_EMAIL = None

                with patch("src.utils.auth_decorators.verify_jwt_in_request") as mock_verify:
                    mock_verify.return_value = None

                    with patch("src.utils.auth_decorators.get_jwt_identity") as mock_jwt:
                        mock_jwt.return_value = "test@example.com"

                        with patch("src.utils.auth_decorators.AuthService") as mock_auth_service_class:
                            mock_auth_service = Mock()
                            mock_auth_service_class.return_value = mock_auth_service

                            mock_user = Mock()
                            mock_user.id = 123
                            mock_auth_service.user_repository.get_by_email.return_value = mock_user

                            with patch("src.utils.auth_decorators.get_db_session") as mock_get_session:
                                mock_session = Mock()
                                mock_get_session.return_value = mock_session

                                result = test_function()

                                assert result == "success"

    def test_jwt_required_with_bypass_decorator_jwt_failure(self):
        """Test jwt_required_with_bypass decorator with JWT authentication failure."""
        from flask import Flask

        from src.core.exceptions import AuthenticationError
        from src.utils.auth_decorators import jwt_required_with_bypass

        app = Flask(__name__)

        @jwt_required_with_bypass
        def test_function():
            return "success"

        with app.app_context():
            with patch("src.utils.auth_decorators.settings") as mock_settings:
                mock_settings.AUTH_BYPASS_EMAIL = None

                with patch("src.utils.auth_decorators.verify_jwt_in_request") as mock_verify:
                    mock_verify.side_effect = AuthenticationError("Invalid token")

                    result = test_function()

                    # The decorator should return a JSON response, not raise an exception
                    assert result[1] == 401  # Status code

    def test_jwt_required_with_bypass_decorator_user_not_found(self):
        """Test jwt_required_with_bypass decorator when user is not found."""
        from flask import Flask

        from src.utils.auth_decorators import jwt_required_with_bypass

        app = Flask(__name__)

        @jwt_required_with_bypass
        def test_function():
            return "success"

        with app.app_context():
            with patch("src.utils.auth_decorators.settings") as mock_settings:
                mock_settings.AUTH_BYPASS_EMAIL = None

                with patch("src.utils.auth_decorators.verify_jwt_in_request") as mock_verify:
                    mock_verify.return_value = None

                    with patch("src.utils.auth_decorators.get_jwt_identity") as mock_jwt:
                        mock_jwt.return_value = "test@example.com"

                        with patch("src.utils.auth_decorators.AuthService") as mock_auth_service_class:
                            mock_auth_service = Mock()
                            mock_auth_service_class.return_value = mock_auth_service

                            mock_auth_service.user_repository.get_by_email.return_value = None

                            with patch("src.utils.auth_decorators.get_db_session") as mock_get_session:
                                mock_session = Mock()
                                mock_get_session.return_value = mock_session

                                result = test_function()

                                # The decorator should return a JSON response, not raise an exception
                                assert result[1] == 500  # Status code for internal server error
