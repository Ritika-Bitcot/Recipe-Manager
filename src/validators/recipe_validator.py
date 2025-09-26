"""Recipe validation for the Recipe Manager API."""

from typing import Any, Dict, List, Optional

from src.core.exceptions import ValidationError


def validate_recipe_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate recipe data and return validated data.

    Args:
        data: Recipe data dictionary

    Returns:
        Validated recipe data

    Raises:
        ValidationError: If recipe data is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Recipe data must be a dictionary", "recipe_data")

    validated_data = {}

    # Validate title
    title = data.get("title")
    if not title:
        raise ValidationError("Recipe title is required", "title")

    validated_data["title"] = validate_string_length(title, "Recipe title", min_length=1, max_length=200)

    # Validate description (optional)
    description = data.get("description")
    if description is not None:
        validated_data["description"] = validate_optional_string(description, "Recipe description", max_length=2000)

    # Validate ingredients
    ingredients = data.get("ingredients")
    if not ingredients:
        raise ValidationError("Recipe ingredients are required", "ingredients")

    if not isinstance(ingredients, list):
        raise ValidationError("Ingredients must be a list", "ingredients")

    if len(ingredients) == 0:
        raise ValidationError("Recipe must have at least one ingredient", "ingredients")

    validated_data["ingredients"] = validate_ingredients_list(ingredients)

    # Validate instructions
    instructions = data.get("instructions")
    if not instructions:
        raise ValidationError("Recipe instructions are required", "instructions")

    if not isinstance(instructions, list):
        raise ValidationError("Instructions must be a list", "instructions")

    if len(instructions) == 0:
        raise ValidationError("Recipe must have at least one instruction", "instructions")

    validated_data["instructions"] = validate_instructions_list(instructions)

    # Validate prep_time (optional)
    prep_time = data.get("prep_time")
    if prep_time is not None:
        validated_data["prep_time"] = validate_positive_integer(prep_time, "Preparation time")

    # Validate cook_time (optional)
    cook_time = data.get("cook_time")
    if cook_time is not None:
        validated_data["cook_time"] = validate_positive_integer(cook_time, "Cooking time")

    # Validate servings (optional)
    servings = data.get("servings")
    if servings is not None:
        validated_data["servings"] = validate_positive_integer(servings, "Servings")

    # Validate difficulty (optional)
    difficulty = data.get("difficulty")
    if difficulty is not None:
        validated_data["difficulty"] = validate_difficulty(difficulty)

    # Validate tags (optional)
    tags = data.get("tags")
    if tags is not None:
        validated_data["tags"] = validate_tags(tags)

    return validated_data


def validate_ingredients_list(ingredients: List[Any]) -> List[str]:
    """Validate ingredients list.

    Args:
        ingredients: List of ingredients

    Returns:
        Validated list of ingredient strings

    Raises:
        ValidationError: If ingredients are invalid
    """
    if not isinstance(ingredients, list):
        raise ValidationError("Ingredients must be a list", "ingredients")

    if len(ingredients) == 0:
        raise ValidationError("Recipe must have at least one ingredient", "ingredients")

    if len(ingredients) > 50:
        raise ValidationError("Recipe cannot have more than 50 ingredients", "ingredients")

    validated_ingredients = []
    for i, ingredient in enumerate(ingredients):
        if not isinstance(ingredient, str):
            raise ValidationError(f"Ingredient {i+1} must be a string", f"ingredients[{i}]")

        validated_ingredient = validate_string_length(ingredient, f"Ingredient {i+1}", min_length=1, max_length=200)
        validated_ingredients.append(validated_ingredient)

    return validated_ingredients


def validate_instructions_list(instructions: List[Any]) -> List[str]:
    """Validate instructions list.

    Args:
        instructions: List of instructions

    Returns:
        Validated list of instruction strings

    Raises:
        ValidationError: If instructions are invalid
    """
    if not isinstance(instructions, list):
        raise ValidationError("Instructions must be a list", "instructions")

    if len(instructions) == 0:
        raise ValidationError("Recipe must have at least one instruction", "instructions")

    if len(instructions) > 100:
        raise ValidationError("Recipe cannot have more than 100 instructions", "instructions")

    validated_instructions = []
    for i, instruction in enumerate(instructions):
        if not isinstance(instruction, str):
            raise ValidationError(f"Instruction {i+1} must be a string", f"instructions[{i}]")

        validated_instruction = validate_string_length(instruction, f"Instruction {i+1}", min_length=1, max_length=1000)
        validated_instructions.append(validated_instruction)

    return validated_instructions


def validate_difficulty(difficulty: Any) -> str:
    """Validate difficulty level.

    Args:
        difficulty: Difficulty level

    Returns:
        Validated difficulty level

    Raises:
        ValidationError: If difficulty is invalid
    """
    if not isinstance(difficulty, str):
        raise ValidationError("Difficulty must be a string", "difficulty")

    valid_difficulties = ["easy", "medium", "hard"]
    if difficulty.lower() not in valid_difficulties:
        raise ValidationError(f"Difficulty must be one of: {', '.join(valid_difficulties)}", "difficulty")

    return difficulty.lower()


def validate_tags(tags: Any) -> List[str]:
    """Validate tags list.

    Args:
        tags: List of tags

    Returns:
        Validated list of tag strings

    Raises:
        ValidationError: If tags are invalid
    """
    if not isinstance(tags, list):
        raise ValidationError("Tags must be a list", "tags")

    if len(tags) > 20:
        raise ValidationError("Recipe cannot have more than 20 tags", "tags")

    validated_tags = []
    for i, tag in enumerate(tags):
        if not isinstance(tag, str):
            raise ValidationError(f"Tag {i+1} must be a string", f"tags[{i}]")

        validated_tag = validate_string_length(tag, f"Tag {i+1}", min_length=1, max_length=50)
        validated_tags.append(validated_tag)

    return validated_tags


def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
    """Validate string length.

    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        min_length: Minimum length
        max_length: Maximum length

    Returns:
        Validated string

    Raises:
        ValidationError: If string length is invalid
    """
    if not value:
        raise ValidationError(f"{field_name} is required", field_name)

    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long", field_name)

    if len(value) > max_length:
        raise ValidationError(f"{field_name} must be less than {max_length} characters", field_name)

    return value.strip()


def validate_positive_integer(value: Any, field_name: str) -> int:
    """Validate positive integer.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated positive integer

    Raises:
        ValidationError: If value is not a valid positive integer
    """
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError(f"{field_name} must be a positive integer", field_name)
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid integer", field_name)


def validate_optional_string(value: Optional[str], field_name: str, max_length: int = 1000) -> Optional[str]:
    """Validate optional string.

    Args:
        value: Optional string value
        field_name: Name of the field for error messages
        max_length: Maximum length

    Returns:
        Validated string or None

    Raises:
        ValidationError: If string length exceeds maximum
    """
    if value is None:
        return None

    if len(value) > max_length:
        raise ValidationError(f"{field_name} must be less than {max_length} characters", field_name)

    return value.strip() if value else None
