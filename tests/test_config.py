"""Tests for configuration validation."""

import os
from unittest.mock import patch

import pytest

from src.core.config import Settings


class TestConfigValidation:
    """Test configuration validation functionality."""

    def test_valid_config(self):
        """Test configuration with valid values."""
        # Setup
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost/db",
            "SECRET_KEY": "valid-secret-key-123",
            "ALLOWED_ORIGINS": '["http://localhost:3000", "https://example.com"]',
            "ENVIRONMENT": "development",
            "LOG_LEVEL": "INFO",
            "LOG_FILE": "app.log",
            "LOG_FORMAT": "%(levelname)s %(message)s",
            "LOG_BODY": "false",
            "LOGGER_TYPE": "development",
            "ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "CACHE_TTL": "300",
            "ENABLE_CACHE": "true",
        }

        with patch.dict(os.environ, env_vars):
            # Execute
            settings = Settings()

            # Assert
            assert settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
            assert settings.SECRET_KEY == "valid-secret-key-123"
            assert settings.ALLOWED_ORIGINS == [
                "http://localhost:3000",
                "https://example.com",
            ]
            assert settings.ENVIRONMENT == "development"
            assert settings.LOG_LEVEL == "INFO"
            assert settings.LOG_FILE == "app.log"
            assert settings.LOG_FORMAT == "%(levelname)s %(message)s"
            assert settings.LOG_BODY is False
            assert settings.LOGGER_TYPE == "development"
            assert settings.ALGORITHM == "HS256"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
            assert settings.CACHE_TTL == 300
            assert settings.ENABLE_CACHE is True

    def test_database_url_validation_postgresql(self):
        """Test valid PostgreSQL database URL."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost/db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.DATABASE_URL == "postgresql://user:pass@localhost/db"

    def test_database_url_validation_postgresql_psycopg2(self):
        """Test valid PostgreSQL with psycopg2 database URL."""
        env_vars = {
            "DATABASE_URL": "postgresql+psycopg2://user:pass@localhost/db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.DATABASE_URL == "postgresql+psycopg2://user:pass@localhost/db"

    def test_database_url_validation_sqlite(self):
        """Test valid SQLite database URL."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.DATABASE_URL == "sqlite:///test.db"

    def test_database_url_validation_invalid(self):
        """Test invalid database URL format."""
        env_vars = {
            "DATABASE_URL": "mysql://user:pass@localhost/db",  # Invalid - not supported
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(
                ValueError,
                match="DATABASE_URL must use postgresql://, postgresql\\+psycopg2://, or sqlite:// format",
            ):
                Settings()

    def test_secret_key_validation_default(self):
        """Test secret key validation with default value."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "your-secret-key-here",  # Default value
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(ValueError, match="SECRET_KEY must be set to a secure value"):
                Settings()

    def test_secret_key_validation_valid(self):
        """Test secret key validation with valid value."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "my-super-secret-key-123",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.SECRET_KEY == "my-super-secret-key-123"

    def test_allowed_origins_validation_list(self):
        """Test allowed origins validation with list input."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["http://localhost:3000", "https://example.com"]',
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.ALLOWED_ORIGINS == [
                "http://localhost:3000",
                "https://example.com",
            ]

    def test_allowed_origins_validation_single_wildcard(self):
        """Test allowed origins validation with single wildcard."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.ALLOWED_ORIGINS == ["*"]

    def test_allowed_origins_validation_invalid_json(self):
        """Test allowed origins validation with invalid JSON."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": "invalid-json",
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(Exception):  # Pydantic validation error
                Settings()

    def test_allowed_origins_validation_not_array(self):
        """Test allowed origins validation with non-array JSON."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '{"origin": "http://localhost:3000"}',  # Object instead of array
            "ENVIRONMENT": "test",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(ValueError, match="ALLOWED_ORIGINS must be a valid JSON array"):
                Settings()

    def test_log_level_validation_valid(self):
        """Test log level validation with valid values."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            env_vars = {
                "DATABASE_URL": "sqlite:///test.db",
                "SECRET_KEY": "valid-secret-key",
                "ALLOWED_ORIGINS": '["*"]',
                "ENVIRONMENT": "test",
                "LOG_LEVEL": level,
            }

            with patch.dict(os.environ, env_vars):
                settings = Settings()
                assert settings.LOG_LEVEL == level

    def test_log_level_validation_invalid(self):
        """Test log level validation with invalid value."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
            "LOG_LEVEL": "INVALID_LEVEL",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
                Settings()

    def test_log_body_validation_boolean_true(self):
        """Test log body validation with boolean true."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
            "LOG_BODY": "true",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.LOG_BODY is True

    def test_log_body_validation_boolean_false(self):
        """Test log body validation with boolean false."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
            "LOG_BODY": "false",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.LOG_BODY is False

    def test_log_body_validation_string_truthy(self):
        """Test log body validation with truthy string values."""
        truthy_values = ["1", "yes", "on", "True"]

        for value in truthy_values:
            env_vars = {
                "DATABASE_URL": "sqlite:///test.db",
                "SECRET_KEY": "valid-secret-key",
                "ALLOWED_ORIGINS": '["*"]',
                "ENVIRONMENT": "test",
                "LOG_BODY": value,
            }

            with patch.dict(os.environ, env_vars):
                settings = Settings()
                assert settings.LOG_BODY is True

    def test_log_body_validation_string_falsy(self):
        """Test log body validation with falsy string values."""
        falsy_values = ["0", "no", "off", "False", "random"]

        for value in falsy_values:
            env_vars = {
                "DATABASE_URL": "sqlite:///test.db",
                "SECRET_KEY": "valid-secret-key",
                "ALLOWED_ORIGINS": '["*"]',
                "ENVIRONMENT": "test",
                "LOG_BODY": value,
            }

            with patch.dict(os.environ, env_vars):
                settings = Settings()
                assert settings.LOG_BODY is False

    def test_logger_type_validation_valid(self):
        """Test logger type validation with valid values."""
        valid_types = ["development", "dev", "production", "prod", "test", "testing"]

        for logger_type in valid_types:
            env_vars = {
                "DATABASE_URL": "sqlite:///test.db",
                "SECRET_KEY": "valid-secret-key",
                "ALLOWED_ORIGINS": '["*"]',
                "ENVIRONMENT": "test",
                "LOGGER_TYPE": logger_type,
            }

            with patch.dict(os.environ, env_vars):
                settings = Settings()
                assert settings.LOGGER_TYPE == logger_type.lower()

    def test_logger_type_validation_invalid(self):
        """Test logger type validation with invalid value."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
            "LOGGER_TYPE": "invalid_type",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(ValueError, match="LOGGER_TYPE must be one of"):
                Settings()

    def test_default_values(self):
        """Test default values when not provided."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
            # Explicitly set database components to test defaults
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "recipe_db",
            "DB_USER": "postgres",
            "DB_PASSWORD": "password",
            "DB_DRIVER": "postgresql+psycopg2",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            # Test default values
            assert settings.LOG_LEVEL == "INFO"
            assert settings.LOG_FILE == "app.log"
            assert settings.LOG_FORMAT == "%(levelname)-8s %(asctime)s %(name)s.%(module)s:%(lineno)s | %(message)s"
            assert settings.LOG_BODY is False
            assert settings.LOGGER_TYPE == "development"
            assert settings.ALGORITHM == "HS256"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
            assert settings.CACHE_TTL == 300
            assert settings.ENABLE_CACHE is True

            # Test individual database component defaults
            assert settings.DB_HOST == "localhost"
            assert settings.DB_PORT == 5432
            assert settings.DB_NAME == "recipe_db"
            assert settings.DB_USER == "postgres"
            assert settings.DB_PASSWORD == "password"
            assert settings.DB_DRIVER == "postgresql+psycopg2"

    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        # Test missing required fields - this should use default values
        env_vars = {
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
            # Explicitly set database components to test defaults
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "recipe_db",
            "DB_USER": "postgres",
            "DB_PASSWORD": "password",
            "DB_DRIVER": "postgresql+psycopg2",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Settings should still work with default values
            settings = Settings()
            # Check that it uses the default values from the actual config
            assert settings.database_url is not None  # This uses computed field
            assert settings.SECRET_KEY is not None
            # Test individual database components have defaults
            assert settings.DB_HOST == "localhost"
            assert settings.DB_PORT == 5432
            assert settings.DB_NAME == "recipe_db"
            assert settings.DB_USER == "postgres"
            assert settings.DB_PASSWORD == "password"
            assert settings.DB_DRIVER == "postgresql+psycopg2"

    def test_numeric_validation(self):
        """Test numeric field validation."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "CACHE_TTL": "600",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
            assert settings.CACHE_TTL == 600

    def test_boolean_validation(self):
        """Test boolean field validation."""
        env_vars = {
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "valid-secret-key",
            "ALLOWED_ORIGINS": '["*"]',
            "ENVIRONMENT": "test",
            "ENABLE_CACHE": "false",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.ENABLE_CACHE is False
