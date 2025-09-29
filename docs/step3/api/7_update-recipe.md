# Update Recipe API

## Endpoint
- **PUT** `/recipes/{id}`
- **Authentication Required**: Yes (JWT)

---

## Purpose
Allows an authenticated user to update a recipe they own.

---

## Request Body
- **title**: string (optional)
- **description**: string (optional)
- **category**: string (optional)
- **ingredients**: array of strings (optional)
- **instructions**: string (optional)
- **image_url**: string (optional, valid URL if provided)

---

## Response
- **200 OK** on success:
  ```json
  {
    "id": 1,
    "title": "Updated Title",
    "description": "Updated description",
    "category": "Updated category",
    "ingredients": ["updated", "list"],
    "instructions": "Updated instructions",
    "owner_id": 1
  }

## Errors:

**401 Unauthorized** → missing/invalid JWT

**403 Forbidden** → updating someone else's recipe

**404 Not Found** → recipe does not exist

**422 Unprocessable** → invalid input format

## Validations

- Only the owner can update.

- Fields must match expected types.

- Image URL validated if provided.

- JWT must be valid.