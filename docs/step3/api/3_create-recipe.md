# Recipe Creation API

## Endpoint
- **POST** `/api/recipes`
- **Authentication Required**: Yes (JWT)

---

## Purpose
Allows an authenticated user to create a new recipe. The recipe is automatically associated with the authenticated user.

---

## Request Body
```json
{
  "title": "string (required, max 200 characters)",
  "description": "string (optional, max 1000 characters)",
  "ingredients": ["string array (optional, max 50 items)"],
  "instructions": "string (required, max 5000 characters)",
  "prep_time": "integer (optional, minutes, 1-1440)",
  "cook_time": "integer (optional, minutes, 1-1440)",
  "servings": "integer (optional, 1-100)",
  "cuisine": "string (optional, max 50 characters)",
  "difficulty": "string (optional, enum: easy, medium, hard)",
  "image_url": "string (optional, valid URL if provided)"
}
```

---

## Response
- **201 Created** on success:
  ```json
  {
    "message": "Recipe created successfully",
    "recipe": {
      "id": 1,
      "title": "Spaghetti Bolognese",
      "description": "Classic Italian pasta dish with rich meat sauce",
      "ingredients": ["spaghetti", "ground beef", "tomato sauce", "onion", "garlic", "olive oil"],
      "instructions": "1. Cook pasta according to package directions\n2. Brown ground beef in olive oil\n3. Add onions and garlic, cook until soft\n4. Add tomato sauce and simmer for 20 minutes\n5. Serve over pasta with parmesan cheese",
      "prep_time": 15,
      "cook_time": 30,
      "servings": 4,
      "cuisine": "Italian",
      "difficulty": "medium",
      "owner_id": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
  ```

## Errors

- **401 Unauthorized** → missing/invalid JWT
- **422 Unprocessable Entity** → validation errors
- **400 Bad Request** → malformed JSON or missing required fields

## Validations

- **Title**: Required, 1-200 characters
- **Instructions**: Required, 1-5000 characters
- **Description**: Optional, max 1000 characters
- **Ingredients**: Optional array, max 50 items, each max 100 characters
- **Prep Time**: Optional, 1-1440 minutes (24 hours)
- **Cook Time**: Optional, 1-1440 minutes (24 hours)
- **Servings**: Optional, 1-100
- **Cuisine**: Optional, max 50 characters
- **Difficulty**: Optional, must be one of: easy, medium, hard
- **Image URL**: Optional, must be valid URL format if provided

## Features

- **Automatic Ownership**: Recipe is automatically linked to authenticated user
- **Comprehensive Validation**: All fields are validated using Pydantic schemas
- **Cache Invalidation**: Recipe list cache is automatically invalidated
- **Type Safety**: Full type validation for all input fields

## Example Usage

```bash
curl -X POST http://localhost:5000/api/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Chocolate Chip Cookies",
    "description": "Soft and chewy chocolate chip cookies perfect for any occasion",
    "ingredients": [
      "2 1/4 cups all-purpose flour",
      "1 tsp baking soda",
      "1 tsp salt",
      "1 cup butter, softened",
      "3/4 cup granulated sugar",
      "3/4 cup brown sugar",
      "2 large eggs",
      "2 tsp vanilla extract",
      "2 cups chocolate chips"
    ],
    "instructions": "1. Preheat oven to 375°F\n2. Mix flour, baking soda, and salt in bowl\n3. Cream butter and sugars until fluffy\n4. Beat in eggs and vanilla\n5. Gradually blend in flour mixture\n6. Stir in chocolate chips\n7. Drop rounded tablespoons onto ungreased cookie sheets\n8. Bake 9-11 minutes until golden brown",
    "prep_time": 20,
    "cook_time": 11,
    "servings": 24,
    "cuisine": "American",
    "difficulty": "easy"
  }'
```

## Response Codes

- **201**: Recipe created successfully
- **400**: Bad request (malformed JSON, missing required fields)
- **401**: Unauthorized (missing or invalid JWT token)
- **422**: Unprocessable entity (validation errors)