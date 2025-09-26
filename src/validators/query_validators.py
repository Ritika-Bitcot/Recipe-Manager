"""Query parameter validation for the Recipe Manager API."""

from typing import Any, Dict, Optional

from src.core.exceptions import ValidationError


def validate_pagination_params(page: Any = None, per_page: Any = None) -> Dict[str, int]:
    """Validate pagination parameters.

    Args:
        page: Page number (1-based)
        per_page: Number of items per page

    Returns:
        Dictionary with validated pagination parameters

    Raises:
        ValidationError: If pagination parameters are invalid
    """
    validated_params = {}

    # Validate page
    if page is not None:
        try:
            page_int = int(page)
            if page_int < 1:
                raise ValidationError("Page must be a positive integer", "page")
            if page_int > 10000:  # Reasonable upper limit
                raise ValidationError("Page number too large", "page")
            validated_params["page"] = page_int
        except (ValueError, TypeError):
            raise ValidationError("Page must be a valid integer", "page")
    else:
        validated_params["page"] = 1

    # Validate per_page
    if per_page is not None:
        try:
            per_page_int = int(per_page)
            if per_page_int < 1:
                raise ValidationError("Per page must be a positive integer", "per_page")
            if per_page_int > 100:  # Reasonable upper limit
                raise ValidationError("Per page cannot exceed 100", "per_page")
            validated_params["per_page"] = per_page_int
        except (ValueError, TypeError):
            raise ValidationError("Per page must be a valid integer", "per_page")
    else:
        validated_params["per_page"] = 10

    return validated_params


def validate_search_params(
    search: Optional[str] = None,
    difficulty: Optional[str] = None,
    prep_time_max: Optional[Any] = None,
    cook_time_max: Optional[Any] = None,
    tags: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate search parameters.

    Args:
        search: Search query string
        difficulty: Difficulty filter
        prep_time_max: Maximum preparation time in minutes
        cook_time_max: Maximum cooking time in minutes
        tags: Comma-separated tags

    Returns:
        Dictionary with validated search parameters

    Raises:
        ValidationError: If search parameters are invalid
    """
    validated_params = {}

    # Validate search query
    if search is not None:
        if not isinstance(search, str):
            raise ValidationError("Search query must be a string", "search")

        search_trimmed = search.strip()
        if len(search_trimmed) > 200:
            raise ValidationError("Search query is too long", "search")

        validated_params["search"] = search_trimmed if search_trimmed else None
    else:
        validated_params["search"] = None

    # Validate difficulty filter
    if difficulty is not None:
        if not isinstance(difficulty, str):
            raise ValidationError("Difficulty must be a string", "difficulty")

        valid_difficulties = ["easy", "medium", "hard"]
        difficulty_lower = difficulty.lower().strip()

        if difficulty_lower not in valid_difficulties:
            raise ValidationError(
                f"Difficulty must be one of: {', '.join(valid_difficulties)}",
                "difficulty",
            )

        validated_params["difficulty"] = difficulty_lower
    else:
        validated_params["difficulty"] = None

    # Validate prep_time_max
    if prep_time_max is not None:
        try:
            prep_time_int = int(prep_time_max)
            if prep_time_int < 0:
                raise ValidationError("Preparation time must be non-negative", "prep_time_max")
            if prep_time_int > 1440:  # 24 hours in minutes
                raise ValidationError("Preparation time cannot exceed 24 hours", "prep_time_max")
            validated_params["prep_time_max"] = prep_time_int
        except (ValueError, TypeError):
            raise ValidationError("Preparation time must be a valid integer", "prep_time_max")
    else:
        validated_params["prep_time_max"] = None

    # Validate cook_time_max
    if cook_time_max is not None:
        try:
            cook_time_int = int(cook_time_max)
            if cook_time_int < 0:
                raise ValidationError("Cooking time must be non-negative", "cook_time_max")
            if cook_time_int > 1440:  # 24 hours in minutes
                raise ValidationError("Cooking time cannot exceed 24 hours", "cook_time_max")
            validated_params["cook_time_max"] = cook_time_int
        except (ValueError, TypeError):
            raise ValidationError("Cooking time must be a valid integer", "cook_time_max")
    else:
        validated_params["cook_time_max"] = None

    # Validate tags
    if tags is not None:
        if isinstance(tags, list):
            # Handle list of tags
            tag_list = [str(tag).strip() for tag in tags if tag]
        elif isinstance(tags, str):
            # Handle comma-separated string
            tags_trimmed = tags.strip()
            if not tags_trimmed:
                tag_list = []
            else:
                # Split by comma and clean up
                tag_list = [tag.strip() for tag in tags_trimmed.split(",")]
                tag_list = [tag for tag in tag_list if tag]  # Remove empty tags
        else:
            raise ValidationError("Tags must be a string or list", "tags")

        if len(tag_list) > 20:
            raise ValidationError("Cannot filter by more than 20 tags", "tags")

        # Validate each tag
        for i, tag in enumerate(tag_list):
            if len(tag) > 50:
                raise ValidationError(f"Tag {i+1} is too long", f"tags[{i}]")
            if len(tag) < 1:
                raise ValidationError(f"Tag {i+1} cannot be empty", f"tags[{i}]")

        validated_params["tags"] = tag_list
    else:
        validated_params["tags"] = []

    return validated_params


def validate_sort_params(sort_by: Optional[str] = None, sort_order: Optional[str] = None) -> Dict[str, str]:
    """Validate sorting parameters.

    Args:
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)

    Returns:
        Dictionary with validated sort parameters

    Raises:
        ValidationError: If sort parameters are invalid
    """
    validated_params = {}

    # Validate sort_by
    if sort_by is not None:
        if not isinstance(sort_by, str):
            raise ValidationError("Sort field must be a string", "sort_by")

        valid_sort_fields = [
            "title",
            "created_at",
            "updated_at",
            "prep_time",
            "cook_time",
            "difficulty",
        ]
        sort_by_lower = sort_by.lower().strip()

        if sort_by_lower not in valid_sort_fields:
            raise ValidationError(f"Sort field must be one of: {', '.join(valid_sort_fields)}", "sort_by")

        validated_params["sort_by"] = sort_by_lower
    else:
        validated_params["sort_by"] = "created_at"

    # Validate sort_order
    if sort_order is not None:
        if not isinstance(sort_order, str):
            raise ValidationError("Sort order must be a string", "sort_order")

        sort_order_lower = sort_order.lower().strip()
        if sort_order_lower not in ["asc", "desc"]:
            raise ValidationError("Sort order must be 'asc' or 'desc'", "sort_order")

        validated_params["sort_order"] = sort_order_lower
    else:
        validated_params["sort_order"] = "desc"

    return validated_params
