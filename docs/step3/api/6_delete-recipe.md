# Recipe Deletion API

## Endpoint
- **DELETE** `/api/recipes/{id}`
- **Authentication Required**: Yes (JWT)

---

## Purpose
Allows a user to delete a recipe they own. This endpoint enforces multi-tenancy by ensuring users can only delete their own recipes.

---

## Path Parameters
- `id` (required): The unique identifier of the recipe to delete

---

## Response

- **200 OK** on successful deletion:
  ```json
  {
    "message": "Recipe deleted successfully"
  }
  ```

## Errors

- **401 Unauthorized** → missing/invalid JWT
- **403 Forbidden** → trying to delete someone else's recipe
- **404 Not Found** → recipe does not exist
- **400 Bad Request** → invalid recipe ID format

## Validations

- **Ownership Check**: Only the recipe owner can delete the recipe
- **Recipe Existence**: Recipe ID must exist in the database
- **Authentication**: Valid JWT token required
- **Authorization**: User must be the owner of the recipe

## Features

- **Multi-tenancy Enforcement**: Users can only delete their own recipes
- **Cache Invalidation**: Recipe list cache is automatically invalidated after deletion
- **Secure Authorization**: Comprehensive ownership validation
- **Error Handling**: Clear error messages for different failure scenarios

## Example Usage

```bash
# Delete a recipe (must be owned by authenticated user)
curl -X DELETE http://localhost:5000/api/recipes/123 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Response Codes

- **200**: Recipe deleted successfully
- **400**: Bad request (invalid recipe ID format)
- **401**: Unauthorized (missing or invalid JWT token)
- **403**: Forbidden (trying to delete another user's recipe)
- **404**: Not found (recipe does not exist)

## Security Notes

- The API automatically determines the recipe owner from the JWT token
- No user can delete recipes belonging to other users
- All deletion operations are logged for audit purposes
- Cache is automatically invalidated to maintain data consistency
