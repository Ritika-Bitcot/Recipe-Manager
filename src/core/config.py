# src/core/config.py
import json
import os
from typing import List, Optional

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment-specific configuration.

    In test environment (ENVIRONMENT=test), .env files are ignored to ensure
    tests are completely isolated and don't depend on external configuration files.
    """

    model_config = SettingsConfigDict(
        env_file=".env" if not os.environ.get("ENVIRONMENT") == "test" else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database Configuration - Support both individual components and full URL
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "recipe_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_DRIVER: str = "postgresql+psycopg2"

    SECRET_KEY: str
    ALLOWED_ORIGINS: List[str]
    ENVIRONMENT: str
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    LOG_FORMAT: str = "%(levelname)-8s %(asctime)s %(name)s.%(module)s:%(lineno)s | %(message)s"
    LOG_BODY: bool = False
    LOGGER_TYPE: str = "development"

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Caching Configuration
    CACHE_TTL: int = 300  # 5 minutes default TTL
    ENABLE_CACHE: bool = True

    # Authentication Bypass for Development
    AUTH_BYPASS_EMAIL: Optional[str] = None

    @field_validator("AUTH_BYPASS_EMAIL", mode="before")
    @classmethod
    def validate_auth_bypass_email(cls, v):
        """Validate AUTH_BYPASS_EMAIL setting."""
        if v is None or v == "" or v == "None" or v == "null":
            return None
        return v

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def validate_log_level(cls, v):
        """Validate and normalize log level."""
        if isinstance(v, str):
            v = v.upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            return "INFO"
        return v

    @field_validator("LOGGER_TYPE", mode="before")
    @classmethod
    def validate_logger_type(cls, v):
        """Validate and normalize logger type."""
        if isinstance(v, str):
            v = v.lower()
        valid_types = ["development", "dev", "production", "prod", "testing", "test"]
        if v not in valid_types:
            return "development"
        return v

    @computed_field
    @property
    def database_url(self) -> str:
        """Construct DATABASE_URL from individual components if not provided directly."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # Construct URL from individual components
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        if v is None:
            return None
        if not v.startswith(("postgresql://", "postgresql+psycopg2://", "sqlite://")):
            raise ValueError("DATABASE_URL must use postgresql://, postgresql+psycopg2://, " "or sqlite:// format")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if v == "your-secret-key-here":
            raise ValueError("SECRET_KEY must be set to a secure value")
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, list):
            return v
        try:
            origins = json.loads(v)
            if not isinstance(origins, list):
                raise ValueError()
            return origins
        except Exception:
            raise ValueError("ALLOWED_ORIGINS must be a valid JSON array")

    @field_validator("LOG_BODY", mode="before")
    @classmethod
    def parse_log_body(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return False
