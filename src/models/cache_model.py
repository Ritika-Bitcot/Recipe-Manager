"""Cache model for SQLAlchemy caching."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from src.core.database import db


class CacheEntry(db.Model):
    """Cache entry model for storing cached data."""

    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    cache_value = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CacheEntry(key='{self.cache_key}', expires_at='{self.expires_at}')>"

    def is_expired(self):
        """Check if the cache entry is expired."""
        return datetime.utcnow() > self.expires_at
