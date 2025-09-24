# Get All Recipes API

## Endpoint
- **GET** `/recipes`
- **Authentication Required**: Yes (JWT)

---

## Purpose
Retrieve a list of all recipes created by the authenticated user.

---

## Response
- **200 OK** on success:
  ```
  [
    {
      "id": 1,
      "title": "Spaghetti Bolognese",
      "category": "Italian",
      "ingredients": ["pasta", "tomato", "beef"],
      "owner_id": 1
    }
  ]
  ```
## Errors:

**401 Unauthorized** → missing/invalid JWT

## Validations

- Only recipes belonging to current user are returned.

- JWT must be valid.