# 6. System Architecture

## ✅ **IMPLEMENTED SYSTEM ARCHITECTURE**

### Clean Architecture Implementation
The Recipe Manager follows **Clean Architecture** principles with a layered approach, ensuring separation of concerns, testability, and maintainability.

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Flask)                        │
├─────────────────────────────────────────────────────────────┤
│  Routes (auth_routes, recipe_routes, health_routes)         │
│  Request/Response Handling                                  │
│  Authentication & Authorization                             │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer                              │
├─────────────────────────────────────────────────────────────┤
│  AuthService, RecipeService, PasswordService                │
│  Business Logic & Validation                                │
│  Cache Management                                           │
│  Multi-tenancy Enforcement                                  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Repository Layer                             │
├─────────────────────────────────────────────────────────────┤
│  BaseRepository, RecipeRepository, UserRepository           │
│  Data Access Abstraction                                    │
│  Query Optimization                                         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  Model Layer                                │
├─────────────────────────────────────────────────────────────┤
│  SQLAlchemy Models (User, Recipe, CacheEntry)               │
│  Domain Entities                                            │
│  Database Schema                                            │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                         │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (Development) / SQLite (Testing)                │
│  SQLAlchemy ORM                                             │
│  Alembic Migrations                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 **AUTHENTICATION WORKFLOW**

### Complete Authentication Flow
1. **User Registration**: `POST /api/auth/register`
   - Email and password validation using Pydantic
   - Password hashed with bcrypt and salt rounds
   - User stored in database with unique email constraint
   - Return 201 Created with user details

2. **User Login**: `POST /api/auth/login`
   - Credential validation against hashed passwords
   - JWT token generation with user ID, email, and expiry
   - Return 200 OK with access token and metadata

3. **Token Validation**: All protected endpoints
   - JWT token validation on every request
   - User identification from token claims
   - Authorization checks for multi-tenancy

4. **User Logout**: `POST /api/auth/logout`
   - JWT token blacklisting for security
   - Return 200 OK with logout confirmation

![Authentication Diagram](/docs/assets/authentication.png)

## 🍽️ **RECIPE MANAGEMENT WORKFLOW**

### Multi-tenancy Implementation
- **Read Access**: Users can read ALL recipes via `GET /api/recipes`
- **Write Access**: Users can only create, update, or delete their own recipes
- **Security**: Comprehensive ownership validation for all write operations

### Recipe CRUD Operations

#### Create Recipe
- **Endpoint**: `POST /api/recipes`
- **Process**: Authenticated user submits recipe data → validation → stored in DB → linked to user
- **Features**: Comprehensive validation, automatic ownership, cache invalidation

#### Read Recipes
- **Endpoint**: `GET /api/recipes` (all recipes) or `GET /api/recipes/{id}` (specific recipe)
- **Process**: Multi-tenancy read access → pagination/filtering → cached results
- **Features**: Pagination, filtering, searching, sorting, caching

#### Update Recipe
- **Endpoint**: `PUT /api/recipes/{id}`
- **Process**: Ownership validation → field validation → update in DB → cache invalidation
- **Features**: Ownership checks, comprehensive validation, cache management

#### Delete Recipe
- **Endpoint**: `DELETE /api/recipes/{id}`
- **Process**: Ownership validation → delete from DB → cache invalidation
- **Features**: Security validation, automatic cleanup, cache management

![CRUD Workflow Diagram](/docs/assets/curd_workflow.png)

## 🗄️ **DATABASE ARCHITECTURE**

### Current Schema
- **Users → Recipes**: 1:N (one user can have multiple recipes)
- **Cache Entries**: Independent table for caching system

### Database Design
- **User (id, email, password_hash, is_active, created_at, updated_at)**
- **Recipe (id, title, description, ingredients, instructions, prep_time, cook_time, servings, cuisine, difficulty, image_url, owner_id, created_at, updated_at)**
- **CacheEntry (id, cache_key, cache_value, expires_at, created_at)**

![ER Diagram](/docs/assets/er_diagram.png)

## ⚡ **CACHING ARCHITECTURE**

### SQLAlchemy Caching System
- **Database-backed Caching**: Uses `cache_entries` table
- **Automatic Invalidation**: Cache cleared on data changes
- **TTL Management**: Configurable time-to-live for cache entries
- **Pattern-based Deletion**: Bulk cache invalidation capabilities

### Cache Flow
```
Service Method Call
    │
    ▼
┌─────────────────┐
│  Cache Check    │ ← Check if result is cached
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Cache Hit?     │
└─────────────────┘
    │
    ├─ Yes ──► Return Cached Result
    │
    └─ No ──► Execute Business Logic
              │
              ▼
         ┌─────────────────┐
         │  Cache Result   │ ← Store result in cache
         └─────────────────┘
              │
              ▼
         Return Result
```

## 🔒 **SECURITY ARCHITECTURE**

### Multi-layer Security
- **JWT Authentication**: Secure token-based authentication
- **Password Security**: bcrypt hashing with salt rounds
- **Input Validation**: Comprehensive Pydantic validation
- **Multi-tenancy**: Secure read/write access control
- **Error Security**: No information leakage in error responses

### Authorization Flow
```
Request with JWT Token
    │
    ▼
┌───────────────────┐
│  Token Validation │ ← JWT verification
└───────────────────┘
    │
    ▼
┌──────────────────────┐
│  User Identification │ ← Extract user from token
└──────────────────────┘
    │
    ▼
┌─────────────────┐
│  Authorization  │ ← Multi-tenancy checks
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Business Logic │ ← Execute operation
└─────────────────┘
```

## 🧪 **TESTING ARCHITECTURE**

### Test Pyramid
```
┌─────────────────────────────────────────────────────────────┐
│                Integration Tests (20%)                      │
│  API endpoint testing, database integration                 │
├─────────────────────────────────────────────────────────────┤
│                Service Tests (30%)                          │
│  Business logic testing, service layer validation           │
├─────────────────────────────────────────────────────────────┤
│                Unit Tests (50%)                             │
│  Individual component testing, utility functions            │
└─────────────────────────────────────────────────────────────┘
```

### Test Coverage
- **Overall Coverage**: 82% (359 tests)
- **Test Categories**: Authentication, recipe management, caching, validation
- **Database Testing**: SQLite in-memory for fast, isolated testing
- **Integration Testing**: Full API endpoint testing

## 📊 **PERFORMANCE ARCHITECTURE**

### Query Optimization
- **Pagination**: Efficient LIMIT/OFFSET queries
- **Filtering**: Optimized WHERE clauses for search/filter
- **Sorting**: INDEX support for ORDER BY operations
- **Caching**: Database-backed caching for frequently accessed data

### Scalability Features
- **Horizontal Scaling**: Stateless design supports multiple instances
- **Database Separation**: Different databases for different environments
- **Connection Pooling**: Efficient database connection management
- **Async Support**: High-performance async operations where applicable

## 🏗️ **DESIGN PATTERNS**

### SOLID Principles Applied
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes are substitutable for base classes
- **Interface Segregation**: Clients depend only on interfaces they use
- **Dependency Inversion**: Depend on abstractions, not concretions

### Architectural Patterns
- **Repository Pattern**: Data access abstraction
- **Service Layer Pattern**: Business logic encapsulation
- **Interface Segregation**: Focused contract design
- **Dependency Injection**: Loose coupling between components

## 🚀 **DEPLOYMENT ARCHITECTURE**

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   PostgreSQL    │    │   Test Suite    │
│   (Port 5000)   │◄──►│   (Port 5432)   │    │   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Production Considerations
- **Database**: PostgreSQL with connection pooling
- **Caching**: Database-backed caching system
- **Load Balancing**: Multiple Flask instances
- **Monitoring**: Application performance monitoring
- **Security**: HTTPS, rate limiting, input validation

This architecture provides a robust, scalable, and maintainable foundation for the Recipe Manager application with enterprise-grade features and excellent performance characteristics.
