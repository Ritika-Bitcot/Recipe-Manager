"""Recipe model for the Recipe Manager API."""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.core.database import db


class Recipe(db.Model):
    """Recipe model representing a user's recipe."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ingredients = Column(JSON, nullable=False)
    instructions = Column(JSON, nullable=False)
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)
    servings = Column(Integer, nullable=True)
    difficulty = Column(String(20), nullable=True)
    cuisine = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)  # Store as JSON array
    image_url = Column(String(500), nullable=True)
    is_public = Column(String(10), default="private", nullable=False)  # private, public

    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    owner = relationship("User", back_populates="recipes")

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, title='{self.title}', owner_id={self.owner_id})>"

    def to_dict(self) -> dict:
        """Convert recipe to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "prep_time": self.prep_time_minutes,
            "cook_time": self.cook_time_minutes,
            "servings": self.servings,
            "difficulty": self.difficulty,
            "cuisine": self.cuisine,
            "tags": self.tags,
            "image_url": self.image_url,
            "is_public": self.is_public,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
