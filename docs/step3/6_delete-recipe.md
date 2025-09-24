# Recipe Deletion API

## Endpoint
- **DELETE** `/recipes/{id}`
- **Authentication Required**: Yes (JWT)

---

## Purpose
Allows a user to delete a recipe they own.

---

## Response

- **200 OK** on successful deletion:
  ```
  {
    "message": "Recipe deleted successfully"
  }
  ```
## Errors:

**401 Unauthorized** → missing/invalid JWT

**403 Forbidden** → trying to delete someone else's recipe

**404 Not Found** → recipe does not exist

## Validations

- Only the owner can delete.

- Recipe ID must exist and be valid.

- JWT must be valid.
