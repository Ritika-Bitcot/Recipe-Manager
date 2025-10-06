"""Settings instance for the Recipe Manager API."""

from .config import Settings

# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get a fresh settings instance.

    This function creates a new Settings instance, which is useful for testing
    or when you need to reload configuration from environment variables.
    """
    return Settings()
