"""Recipe schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class IngredientSchema(BaseModel):
    """Schema for individual ingredient."""

    name: str = Field(..., min_length=1, max_length=200)
    amount: str = Field(..., min_length=1, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)

    @field_validator("name", "amount")
    @classmethod
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


# Alternative schema for simple string ingredients
class SimpleIngredientSchema(BaseModel):
    """Schema for simple string ingredients."""

    ingredient: str = Field(..., min_length=1, max_length=500)

    @field_validator("ingredient")
    @classmethod
    def validate_ingredient(cls, v):
        if not v or not v.strip():
            raise ValueError("Ingredient cannot be empty")
        return v.strip()


class RecipeBase(BaseModel):
    """Base recipe schema with common fields."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    ingredients: List[str] = Field(..., min_items=1)  # Simple string list
    instructions: List[str] = Field(..., min_items=1)  # List of instruction steps
    prep_time: Optional[int] = Field(None, ge=0, le=1440)  # Max 24 hours
    cook_time: Optional[int] = Field(None, ge=0, le=1440)
    servings: Optional[int] = Field(None, ge=1, le=100)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    cuisine: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None, min_items=1)
    image_url: Optional[str] = Field(None, max_length=500)
    is_public: str = Field("private", pattern="^(private|public)$")

    @field_validator("title")
    @classmethod
    def validate_required_text_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Instructions cannot be empty")
        return [step.strip() for step in v if step.strip()]

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Ingredients cannot be empty")
        return [ingredient.strip() for ingredient in v if ingredient.strip()]

    @field_validator("description", "cuisine")
    @classmethod
    def validate_optional_text_fields(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v.strip() if v else None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            return [tag.strip() for tag in v if tag.strip()]
        return v


class RecipeCreate(RecipeBase):
    """Schema for creating a new recipe."""

    pass


class RecipeUpdate(BaseModel):
    """Schema for updating an existing recipe."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    ingredients: Optional[List[str]] = Field(None, min_items=1)
    instructions: Optional[List[str]] = Field(None, min_items=1)
    prep_time: Optional[int] = Field(None, ge=0, le=1440)
    cook_time: Optional[int] = Field(None, ge=0, le=1440)
    servings: Optional[int] = Field(None, ge=1, le=100)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    cuisine: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None, min_items=1)
    image_url: Optional[str] = Field(None, max_length=500)
    is_public: Optional[str] = Field(None, pattern="^(private|public)$")

    @field_validator("title")
    @classmethod
    def validate_required_text_fields(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Field cannot be empty")
        return v.strip() if v else v

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, v):
        if v is not None:
            if not v or len(v) == 0:
                raise ValueError("Instructions cannot be empty")
            return [step.strip() for step in v if step.strip()]
        return v

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, v):
        if v is not None:
            if not v or len(v) == 0:
                raise ValueError("Ingredients cannot be empty")
            return [ingredient.strip() for ingredient in v if ingredient.strip()]
        return v

    @field_validator("description", "cuisine")
    @classmethod
    def validate_optional_text_fields(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v.strip() if v else v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            return [tag.strip() for tag in v if tag.strip()]
        return v


class RecipeResponse(RecipeBase):
    """Schema for recipe response."""

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecipeListResponse(BaseModel):
    """Schema for recipe list response."""

    recipes: List[RecipeResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
