## Endpoint
- **GET** `/recipes/{id}`
- **Authentication Required**: Yes (JWT)

---

## Purpose
Retrieve a single recipe by ID for the authenticated owner.

---

## Response
- **200 OK** on success:
  ```json
  {
    "id": 1,
    "title": "Spaghetti Bolognese",
    "description": "Classic Italian pasta dish",
    "category": "Italian",
    "ingredients": ["pasta", "tomato", "beef"],
    "instructions": "Boil pasta, cook beef, add sauce",
    "owner_id": 1
  }

## Errors:

**401 Unauthorized** → missing/invalid JWT

**403 Forbidden** → accessing someone else's recipe

**404 Not Found** → recipe does not exist

## Validations
- Recipe must belong to requesting user.

- Recipe ID must be valid integer.

- JWT must be valid.
