# Recipe Creation API

## Endpoint
- **POST** `/recipes`
- **Authentication Required**: Yes (JWT)

---

## Purpose
Allows an authenticated user to create a new recipe.

---

## Request Body
- **title**: string (required)
- **description**: string (optional)
- **category**: string (optional)
- **ingredients**: array of strings (optional)
- **instructions**: string (required)
- **image_url**: string (optional, valid URL if provided)

---

## Response
- **201 Created** on success:
  ```
  {
    "id": 1,
    "title": "Spaghetti Bolognese",
    "description": "Classic Italian pasta dish",
    "category": "Italian",
    "ingredients": ["pasta", "tomato", "beef"],
    "instructions": "Boil pasta, cook beef, add sauce",
    "owner_id": 1
  }
  ```
## Errors:

**401 Unauthorized** → missing/invalid JWT

**422 Unprocessable** → invalid or missing fields

**403 Forbidden** → user trying to create recipe for another user

## Validations

-Title and instructions are required.

-Image URL validated if present.

-Recipe is linked to logged-in user.

-Only authenticated users can create recipes.