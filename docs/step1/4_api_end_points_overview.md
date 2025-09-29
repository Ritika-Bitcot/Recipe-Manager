# 4. API Endpoints Overview

## ✅ **IMPLEMENTED API ENDPOINTS**

### Base URL
- **Development**: `http://localhost:5000`
- **API Version**: `v1.0.0`
- **Authentication**: JWT Bearer Token

### Complete Endpoint Reference

| Endpoint | Method | Auth Required | Description | Multi-tenancy |
|----------|--------|---------------|-------------|---------------|
| `/` | GET | No | API status and version | - |
| `/health` | GET | No | Basic health check | - |
| `/health/ready` | GET | No | Readiness check with DB | - |
| `/api/auth/register` | POST | No | Register new user | - |
| `/api/auth/login` | POST | No | Authenticate user & return JWT | - |
| `/api/auth/logout` | POST | Yes | Logout and invalidate token | - |
| `/api/auth/me` | GET | Yes | Get current user profile | - |
| `/api/recipes` | GET | Yes | List all recipes (paginated) | Read: All, Write: Own |
| `/api/recipes` | POST | Yes | Create a new recipe | Write: Own only |
| `/api/recipes/{id}` | GET | Yes | Get recipe by ID | Read: All |
| `/api/recipes/{id}` | PUT | Yes | Update recipe | Write: Own only |
| `/api/recipes/{id}` | DELETE | Yes | Delete recipe | Write: Own only |

## 🚀 **ADVANCED FEATURES**

### Multi-tenancy Implementation
- **Read Access**: Users can read ALL recipes in the system
- **Write Access**: Users can only create, update, or delete their own recipes
- **Security**: Comprehensive ownership validation for all write operations

### Advanced Query Parameters (GET /api/recipes)
- `page` (optional): Page number for pagination (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)
- `search` (optional): Search by recipe title
- `cuisine` (optional): Filter by cuisine type
- `difficulty` (optional): Filter by difficulty level
- `sort_by` (optional): Sort field (title, created_at, updated_at)
- `sort_order` (optional): Sort order (asc, desc)

### Caching System
- **SQLAlchemy Caching**: Database-backed caching for improved performance
- **Automatic Invalidation**: Cache automatically invalidated on data changes
- **Configurable TTL**: Time-to-live configuration for cache entries

## 📝 **REQUEST/RESPONSE EXAMPLES**

### 1. User Registration
**POST /api/auth/register**
```json
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

**Response (201):**
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
**POST /api/auth/login**
```json
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Create Recipe
**POST /api/recipes**
```json
{
  "title": "Spaghetti Bolognese",
  "description": "Classic Italian pasta dish with rich meat sauce",
  "ingredients": ["spaghetti", "ground beef", "tomato sauce", "onion", "garlic"],
  "instructions": "1. Cook pasta 2. Prepare sauce 3. Combine and serve",
  "prep_time": 20,
  "cook_time": 30,
  "servings": 4,
  "cuisine": "Italian",
  "difficulty": "medium"
}
```

**Response (201):**
```json
{
  "message": "Recipe created successfully",
  "recipe": {
    "id": 1,
    "title": "Spaghetti Bolognese",
    "description": "Classic Italian pasta dish with rich meat sauce",
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
}
```

### 4. Get All Recipes (Multi-tenancy)
**GET /api/recipes?page=1&per_page=10&cuisine=Italian&search=pasta**

**Response (200):**
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

### 5. Get Recipe by ID
**GET /api/recipes/1**

**Response (200):**
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

### 6. Update Recipe
**PUT /api/recipes/1**
```json
{
  "title": "Updated Spaghetti Bolognese",
  "description": "Updated description",
  "ingredients": ["updated", "ingredients"]
}
```

**Response (200):**
```json
{
  "message": "Recipe updated successfully",
  "recipe": {
    "id": 1,
    "title": "Updated Spaghetti Bolognese",
    "description": "Updated description",
    "ingredients": ["updated", "ingredients"],
    "instructions": "1. Cook pasta 2. Prepare sauce 3. Combine",
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
**DELETE /api/recipes/1**

**Response (200):**
```json
{
  "message": "Recipe deleted successfully"
}
```

### 8. User Profile
**GET /api/auth/me**

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### 9. User Logout
**POST /api/auth/logout**

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

## 🚨 **ERROR RESPONSES**

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
- **AUTHENTICATION_ERROR** (401): Invalid or missing JWT token
- **AUTHORIZATION_ERROR** (403): Insufficient permissions
- **RESOURCE_NOT_FOUND** (404): Resource not found
- **VALIDATION_ERROR** (422): Input validation failed
- **INTERNAL_SERVER_ERROR** (500): Unexpected server error

## 🔒 **SECURITY FEATURES**

- **JWT Authentication**: Secure token-based authentication
- **Password Security**: bcrypt hashing with salt rounds
- **Input Validation**: Comprehensive Pydantic validation
- **Multi-tenancy**: Secure read/write access control
- **Error Security**: No information leakage in error responses
- **CORS Support**: Configurable cross-origin resource sharing

## ⚡ **PERFORMANCE FEATURES**

- **Caching System**: SQLAlchemy-based caching with automatic invalidation
- **Pagination**: Efficient handling of large datasets
- **Query Optimization**: Optimized database queries
- **Async Support**: High-performance async operations
- **Database Separation**: Different databases for development and testing