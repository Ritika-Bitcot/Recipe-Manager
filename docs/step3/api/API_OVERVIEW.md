# Recipe Manager API - Complete Overview

## 🚀 API Summary

The Recipe Manager API is a comprehensive RESTful service built with Flask, featuring JWT authentication, multi-tenancy, advanced caching, and full CRUD operations for recipe management.

## 📋 Base Information

- **Base URL**: `http://localhost:5000`
- **API Version**: `v1.0.0`
- **Authentication**: JWT Bearer Token
- **Content Type**: `application/json`
- **Rate Limiting**: None (development)

## 🔐 Authentication

All endpoints except health checks require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

1. **Register** a new user at `POST /api/auth/register`
2. **Login** at `POST /api/auth/login` to receive a JWT token
3. Use the token in subsequent requests

## 📚 Complete API Reference

### Health & Status

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API status and version | No |
| GET | `/health` | Basic health check | No |
| GET | `/health/ready` | Readiness check with DB | No |

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get token | No |
| POST | `/api/auth/logout` | Logout (blacklist token) | Yes |
| GET | `/api/auth/me` | Get current user profile | Yes |

### Recipe Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/recipes` | Get all recipes (paginated) | Yes |
| GET | `/api/recipes/{id}` | Get recipe by ID | Yes |
| POST | `/api/recipes` | Create new recipe | Yes |
| PUT | `/api/recipes/{id}` | Update recipe (owner only) | Yes |
| DELETE | `/api/recipes/{id}` | Delete recipe (owner only) | Yes |

## 🔍 Detailed Endpoint Documentation

### 1. User Registration

**POST** `/api/auth/register`

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (201)**:
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 2. User Login

**POST** `/api/auth/login`

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Get All Recipes

**GET** `/api/recipes`

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)
- `search` (optional): Search by title
- `cuisine` (optional): Filter by cuisine
- `difficulty` (optional): Filter by difficulty
- `sort_by` (optional): Sort field (title, created_at, updated_at)
- `sort_order` (optional): Sort order (asc, desc)

**Response (200)**:
```json
{
  "recipes": [
    {
      "id": 1,
      "title": "Spaghetti Bolognese",
      "description": "Classic Italian pasta dish",
      "ingredients": ["spaghetti", "ground beef", "tomato sauce"],
      "instructions": "1. Cook pasta 2. Prepare sauce 3. Combine",
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

### 4. Get Recipe by ID

**GET** `/api/recipes/{id}`

**Response (200)**:
```json
{
  "id": 1,
  "title": "Spaghetti Bolognese",
  "description": "Classic Italian pasta dish",
  "ingredients": ["spaghetti", "ground beef", "tomato sauce"],
  "instructions": "1. Cook pasta 2. Prepare sauce 3. Combine",
  "prep_time": 20,
  "cook_time": 30,
  "servings": 4,
  "cuisine": "Italian",
  "difficulty": "medium",
  "owner_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 5. Create Recipe

**POST** `/api/recipes`

```json
{
  "title": "Chocolate Chip Cookies",
  "description": "Soft and chewy cookies",
  "ingredients": ["flour", "sugar", "chocolate chips"],
  "instructions": "1. Mix ingredients 2. Bake at 375°F",
  "prep_time": 20,
  "cook_time": 11,
  "servings": 24,
  "cuisine": "American",
  "difficulty": "easy"
}
```

**Response (201)**:
```json
{
  "message": "Recipe created successfully",
  "recipe": {
    "id": 2,
    "title": "Chocolate Chip Cookies",
    "description": "Soft and chewy cookies",
    "ingredients": ["flour", "sugar", "chocolate chips"],
    "instructions": "1. Mix ingredients 2. Bake at 375°F",
    "prep_time": 20,
    "cook_time": 11,
    "servings": 24,
    "cuisine": "American",
    "difficulty": "easy",
    "owner_id": 1,
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

### 6. Update Recipe

**PUT** `/api/recipes/{id}`

```json
{
  "title": "Updated Recipe Title",
  "description": "Updated description",
  "ingredients": ["updated", "ingredients"],
  "instructions": "Updated instructions"
}
```

**Response (200)**:
```json
{
  "message": "Recipe updated successfully",
  "recipe": {
    "id": 1,
    "title": "Updated Recipe Title",
    "description": "Updated description",
    "ingredients": ["updated", "ingredients"],
    "instructions": "Updated instructions",
    "prep_time": 20,
    "cook_time": 30,
    "servings": 4,
    "cuisine": "Italian",
    "difficulty": "medium",
    "owner_id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:15:00Z"
  }
}
```

### 7. Delete Recipe

**DELETE** `/api/recipes/{id}`

**Response (200)**:
```json
{
  "message": "Recipe deleted successfully"
}
```

## 🚨 Error Responses

All errors follow a consistent format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human readable error message",
  "status_code": 400,
  "details": "Additional error details (optional)"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing JWT token |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |

## 🔒 Multi-tenancy

The API implements multi-tenancy with the following rules:

- **Read Access**: Users can read all recipes in the system
- **Write Access**: Users can only create, update, or delete their own recipes
- **Ownership**: Recipes are automatically associated with the authenticated user
- **Security**: All write operations validate ownership before proceeding

## ⚡ Performance Features

### Caching
- **SQLAlchemy-based caching**: Database-backed cache storage
- **Automatic invalidation**: Cache cleared on data changes
- **Configurable TTL**: 5-minute default cache lifetime
- **Pattern-based deletion**: Bulk cache invalidation

### Pagination
- **Efficient queries**: Database-level pagination
- **Configurable limits**: 1-100 items per page
- **Metadata included**: Total count and page information

## 📊 Rate Limiting & Quotas

Currently no rate limiting is implemented (development mode).

## 🔧 Development & Testing

### Local Development
```bash
# Start the server
python -m src.api.app

# Run tests
pytest --cov=src

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Test Coverage
- **Overall Coverage**: 82%
- **Total Tests**: 359
- **Test Categories**: Unit, Integration, Repository, Caching, Authentication

## 📝 Request/Response Examples

### Complete Workflow

1. **Register User**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "chef@example.com", "password": "SecurePass123!"}'
```

2. **Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "chef@example.com", "password": "SecurePass123!"}'
```

3. **Create Recipe**
```bash
curl -X POST http://localhost:5000/api/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title": "Pasta", "instructions": "Cook pasta"}'
```

4. **Get All Recipes**
```bash
curl -X GET "http://localhost:5000/api/recipes?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛠️ Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ALLOWED_ORIGINS`: CORS allowed origins
- `ENVIRONMENT`: Environment (dev/test/prod)
- `CACHE_TTL`: Cache time-to-live in seconds
- `ENABLE_CACHE`: Enable/disable caching

### Database
- **Development**: PostgreSQL
- **Testing**: SQLite in-memory
- **Migrations**: Alembic for schema management
