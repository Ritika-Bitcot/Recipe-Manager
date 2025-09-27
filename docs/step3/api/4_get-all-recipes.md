# Get All Recipes API

## Endpoint
- **GET** `/api/recipes`
- **Authentication Required**: Yes (JWT)

---

## Purpose
Retrieve a paginated list of all recipes in the system. This endpoint implements multi-tenancy where users can read all recipes but can only modify their own.

---

## Query Parameters
- `page` (optional): Page number for pagination (default: 1)
- `per_page` (optional): Number of recipes per page (default: 10, max: 100)
- `search` (optional): Search term to filter recipes by title
- `cuisine` (optional): Filter recipes by cuisine type
- `difficulty` (optional): Filter recipes by difficulty level
- `sort_by` (optional): Sort field (title, created_at, updated_at)
- `sort_order` (optional): Sort order (asc, desc)

---

## Response
- **200 OK** on success:
  ```json
  {
    "recipes": [
      {
        "id": 1,
        "title": "Spaghetti Bolognese",
        "description": "Classic Italian pasta dish",
        "ingredients": ["spaghetti", "ground beef", "tomato sauce", "onion", "garlic"],
        "instructions": "1. Cook pasta 2. Prepare sauce 3. Combine and serve",
        "prep_time": 20,
        "cook_time": 30,
        "servings": 4,
        "cuisine": "Italian",
        "difficulty": "medium",
        "owner_id": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 25,
      "pages": 3
    }
  }
  ```

## Errors

- **401 Unauthorized** → missing/invalid JWT
- **400 Bad Request** → invalid query parameters
- **422 Unprocessable Entity** → validation errors

## Features

- **Multi-tenancy**: Users can read all recipes but only modify their own
- **Pagination**: Efficient handling of large recipe collections
- **Search**: Full-text search by recipe title
- **Filtering**: Filter by cuisine, difficulty, and other attributes
- **Sorting**: Sort by various fields in ascending or descending order
- **Caching**: Results are cached for improved performance

## Example Usage

```bash
# Get first page of recipes
curl -X GET "http://localhost:5000/api/recipes" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get second page with 20 recipes per page
curl -X GET "http://localhost:5000/api/recipes?page=2&per_page=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Search for Italian recipes
curl -X GET "http://localhost:5000/api/recipes?cuisine=Italian&search=pasta" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Sort by title in descending order
curl -X GET "http://localhost:5000/api/recipes?sort_by=title&sort_order=desc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```