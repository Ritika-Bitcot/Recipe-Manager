"""SQLAlchemy-based caching service."""

import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional

from src.core.config import Settings
from src.core.structured_logging import get_logger, log_cache_operation

logger = get_logger(__name__)
settings = Settings()


class CacheService:
    """SQLAlchemy-based caching service using database for caching."""

    def __init__(self):
        self.enabled = settings.ENABLE_CACHE
        self.cache_table = None
        self._initialized = False

        if self.enabled:
            logger.info("SQLAlchemy cache service initialized")
        else:
            logger.info("Caching disabled by configuration")

    def _ensure_initialized(self):
        """Ensure cache table is initialized."""
        if not self.enabled or self._initialized:
            return

        try:
            from flask import current_app

            from src.core.database import db
            from src.models.cache_model import CacheEntry

            # Only initialize if we're in an app context
            try:
                app = current_app
                if not app:
                    logger.warning("No Flask app context available for cache initialization")
                    self.enabled = False
                    return
            except RuntimeError:
                logger.warning("No Flask app context available for cache initialization")
                self.enabled = False
                return

            # Set the cache table
            self.cache_table = CacheEntry
            self._initialized = True

            # Create the table if it doesn't exist
            db.create_all()
            logger.info("Cache table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cache table: {e}")
            self.enabled = False

    def _initialize_cache_table(self):
        """Initialize cache table if not exists."""
        if not self.enabled:
            return

        try:
            from flask import current_app

            from src.core.database import db
            from src.models.cache_model import CacheEntry

            # Only initialize if we're in an app context
            try:
                app = current_app
                if not app:
                    logger.warning("No Flask app context available for cache initialization")
                    self.enabled = False
                    return
            except RuntimeError:
                logger.warning("No Flask app context available for cache initialization")
                self.enabled = False
                return

            # Set the cache table
            self.cache_table = CacheEntry

            # Create the table if it doesn't exist
            db.create_all()
            logger.info("Cache table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cache table: {e}")
            self.enabled = False

    def _serialize(self, value: Any) -> str:
        """Serialize value for storage."""
        import json

        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage."""
        import json

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        start_time = time.time()

        if not self.enabled:
            return None

        self._ensure_initialized()

        if not self.cache_table:
            return None

        try:
            from src.core.database import get_db_session

            session = get_db_session()

            # Get cache entry
            cache_entry = (
                session.query(self.cache_table)
                .filter(
                    self.cache_table.cache_key == key,
                    self.cache_table.expires_at > datetime.utcnow(),
                )
                .first()
            )

            hit = cache_entry is not None
            duration = time.time() - start_time

            log_cache_operation(
                logger=logger,
                operation="get",
                key=key,
                hit=hit,
                duration_ms=round(duration * 1000, 2),
            )

            if cache_entry:
                return self._deserialize(cache_entry.cache_value)

            return None

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Cache get operation failed",
                extra={
                    "operation": "get",
                    "key": key,
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2),
                },
            )
            return None
        finally:
            if "session" in locals():
                session.close()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        start_time = time.time()

        if not self.enabled:
            return False

        self._ensure_initialized()

        if not self.cache_table:
            return False

        try:
            from src.core.database import get_db_session

            session = get_db_session()

            ttl = ttl or settings.CACHE_TTL
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            serialized_value = self._serialize(value)

            # Check if key exists
            existing_entry = session.query(self.cache_table).filter(self.cache_table.cache_key == key).first()

            is_update = existing_entry is not None

            if existing_entry:
                # Update existing entry
                existing_entry.cache_value = serialized_value
                existing_entry.expires_at = expires_at
            else:
                # Create new entry
                cache_entry = self.cache_table(cache_key=key, cache_value=serialized_value, expires_at=expires_at)
                session.add(cache_entry)

            session.commit()

            duration = time.time() - start_time
            log_cache_operation(
                logger=logger,
                operation="set",
                key=key,
                hit=False,  # Set operations are not hits
                duration_ms=round(duration * 1000, 2),
                ttl=ttl,
                is_update=is_update,
            )

            return True

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Cache set operation failed",
                extra={
                    "operation": "set",
                    "key": key,
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2),
                    "ttl": ttl,
                },
            )
            if "session" in locals():
                session.rollback()
            return False
        finally:
            if "session" in locals():
                session.close()

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled:
            return False

        self._ensure_initialized()

        if not self.cache_table:
            return False

        try:
            from src.core.database import get_db_session

            session = get_db_session()

            result = session.query(self.cache_table).filter(self.cache_table.cache_key == key).delete()

            session.commit()
            log_cache_operation(
                logger=logger,
                operation="delete",
                key=key,
                hit=False,
                deleted_count=result,
            )
            return bool(result)

        except Exception as e:
            logger.error(
                "Cache delete operation failed",
                operation="delete",
                key=key,
                error=str(e),
            )
            if "session" in locals():
                session.rollback()
            return False
        finally:
            if "session" in locals():
                session.close()

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled:
            return 0

        self._ensure_initialized()

        if not self.cache_table:
            return 0

        try:
            from src.core.database import get_db_session

            session = get_db_session()

            # SQLAlchemy doesn't have pattern matching like Redis, so we'll use LIKE
            pattern_sql = pattern.replace("*", "%")
            result = session.query(self.cache_table).filter(self.cache_table.cache_key.like(pattern_sql)).delete()

            session.commit()
            logger.debug(f"Cache delete pattern: {pattern} ({result} keys)")
            return result

        except Exception as e:
            logger.error(f"Cache error deleting pattern {pattern}: {e}")
            if "session" in locals():
                session.rollback()
            return 0
        finally:
            if "session" in locals():
                session.close()

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.enabled:
            return False

        self._ensure_initialized()

        if not self.cache_table:
            return False

        try:
            from src.core.database import get_db_session

            session = get_db_session()

            exists = (
                session.query(self.cache_table)
                .filter(
                    self.cache_table.cache_key == key,
                    self.cache_table.expires_at > datetime.utcnow(),
                )
                .first()
                is not None
            )

            return exists

        except Exception as e:
            logger.error(f"Cache error checking key {key}: {e}")
            return False
        finally:
            if "session" in locals():
                session.close()

    def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        if not self.enabled:
            return 0

        self._ensure_initialized()

        if not self.cache_table:
            return 0

        try:
            from src.core.database import get_db_session

            session = get_db_session()

            result = session.query(self.cache_table).filter(self.cache_table.expires_at <= datetime.utcnow()).delete()

            session.commit()
            logger.debug(f"Cleaned up {result} expired cache entries")
            return result

        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            if "session" in locals():
                session.rollback()
            return 0
        finally:
            if "session" in locals():
                session.close()


def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from prefix and arguments."""
    import json

    key_parts = [prefix]

    # Add positional arguments
    for arg in args:
        if isinstance(arg, (dict, list)):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(arg))

    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (dict, list)):
            key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        else:
            key_parts.append(f"{k}:{v}")

    return ":".join(key_parts)


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator for caching function results."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = CacheService()

            # Generate cache key
            func_name = key_prefix or func.__name__
            cache_key_str = cache_key(func_name, *args, **kwargs)

            # Try to get from cache
            cached_result = cache.get(cache_key_str)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key_str, result, ttl)
            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """Decorator for invalidating cache after function execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Invalidate cache
            cache = CacheService()
            cache.delete_pattern(pattern)

            return result

        return wrapper

    return decorator


# Global cache instance
cache_service = CacheService()
