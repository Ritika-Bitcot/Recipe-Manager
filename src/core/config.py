# src/core/config.py
import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgresql+psycopg2://", "sqlite://")):
            raise ValueError("DATABASE_URL must use postgresql://, postgresql+psycopg2://, or sqlite:// format")
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

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    @field_validator("LOG_BODY", mode="before")
    @classmethod
    def parse_log_body(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return False

    @field_validator("LOGGER_TYPE")
    @classmethod
    def validate_logger_type(cls, v):
        valid_types = ["development", "dev", "production", "prod", "test", "testing"]
        if v.lower() not in valid_types:
            raise ValueError(f"LOGGER_TYPE must be one of {valid_types}")
        return v.lower()
