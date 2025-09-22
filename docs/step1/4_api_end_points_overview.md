# 4. API Endpoints Overview

| Endpoint          | Method | Auth Required | Description                        |
|-------------------|--------|---------------|------------------------------------|
| /auth/register    | POST   | No            | Register new user                  |
| /auth/login       | POST   | No            | Authenticate user & return JWT     |
| /recipes          | GET    | Yes           | List all recipes for logg-in user  |
| /recipes          | POST   | Yes           | Create a new recipe                |
| /recipes/{id}     | GET    | Yes           | Get a single recipe (owner only)   |
| /recipes/{id}     | PUT    | Yes           | Update a recipe (owner only)       |
| /recipes/{id}     | DELETE | Yes           | Delete a recipe (owner only)       |

## Request/Response Examples

### User Registration
**POST /auth/register**
```
{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```
**Response (201):**
```
{
  "message": "User registered successfully"
}
```
### User Login

**POST /auth/login**
```
{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```

**Response (200):**
```
{
  "access_token": "jwt_token_string",
  "token_type": "bearer"
}
```

### Create Recipe

**POST /recipes**
```
{
  "title": "Spaghetti Bolognese",
  "description": "Classic Italian pasta dish",
  "category": "Italian",
  "ingredients": ["pasta", "tomato", "beef"],
  "instructions": "Boil pasta, cook beef, add sauce"
}
```

**Response (201):**
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