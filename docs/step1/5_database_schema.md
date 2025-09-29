# 5. Database Schema Design

## ✅ **IMPLEMENTED DATABASE SCHEMA**

### Database Architecture
- **Development**: PostgreSQL (ACID-compliant, production-ready)
- **Testing**: SQLite in-memory (fast, isolated testing)
- **Migrations**: Alembic for schema version control
- **Caching**: Database-backed caching system

## 📊 **IMPLEMENTED TABLES**

### users
| Column        | Type      | Constraints                    | Description |
|---------------|-----------|--------------------------------|-------------|
| id            | SERIAL    | PK, AUTO_INCREMENT             | Primary key |
| email         | VARCHAR   | UNIQUE, NOT NULL               | User email (unique) |
| password_hash | VARCHAR   | NOT NULL                       | bcrypt hashed password |
| is_active     | BOOLEAN   | DEFAULT TRUE, NOT NULL         | Account status |
| created_at    | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP      | Account creation time |
| updated_at    | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP      | Last update time |

### recipes
| Column        | Type      | Constraints                    | Description |
|---------------|-----------|--------------------------------|-------------|
| id            | SERIAL    | PK, AUTO_INCREMENT             | Primary key |
| title         | VARCHAR   | NOT NULL, MAX 200 CHARS        | Recipe title |
| description   | TEXT      | NULL, MAX 1000 CHARS           | Recipe description |
| ingredients   | JSON      | NULL                           | Ingredients as JSON array |
| instructions  | TEXT      | NOT NULL, MAX 5000 CHARS       | Cooking instructions |
| prep_time     | INTEGER   | NULL, 1-1440 MINUTES           | Preparation time |
| cook_time     | INTEGER   | NULL, 1-1440 MINUTES           | Cooking time |
| servings      | INTEGER   | NULL, 1-100                    | Number of servings |
| cuisine       | VARCHAR   | NULL, MAX 50 CHARS             | Cuisine type |
| difficulty    | VARCHAR   | NULL, ENUM(easy,medium,hard)   | Difficulty level |
| image_url     | VARCHAR   | NULL, VALID URL                | Recipe image URL |
| owner_id      | INTEGER   | FK → users(id), NOT NULL       | Recipe owner |
| created_at    | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP      | Creation time |
| updated_at    | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP      | Last update time |

### cache_entries
| Column        | Type      | Constraints                    | Description |
|---------------|-----------|--------------------------------|-------------|
| id            | SERIAL    | PK, AUTO_INCREMENT             | Primary key |
| cache_key     | VARCHAR   | UNIQUE, NOT NULL, INDEX        | Cache key |
| cache_value   | TEXT      | NOT NULL                       | Cached value (JSON) |
| expires_at    | TIMESTAMP | NOT NULL, INDEX                | Expiration time |
| created_at    | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP      | Creation time |

## 🔗 **RELATIONSHIPS**

### Primary Relationships
- **Users → Recipes**: 1:N (one user can have multiple recipes)
- **Cache Entries**: Independent table for caching system

### Foreign Key Constraints
- **recipes.owner_id** → **users.id** (CASCADE on user deletion)
- **Indexes**: Optimized for query performance

## 🚀 **ADVANCED FEATURES**

### Multi-tenancy Support
- **Read Access**: Users can read all recipes via `GET /api/recipes`
- **Write Access**: Users can only modify their own recipes
- **Ownership Validation**: Enforced at service layer and database level

### Caching System
- **Database-backed Caching**: Uses `cache_entries` table
- **Automatic Invalidation**: Cache cleared on data changes
- **TTL Management**: Configurable time-to-live for cache entries
- **Pattern-based Deletion**: Bulk cache invalidation capabilities

### Data Validation
- **Field Constraints**: Comprehensive validation at database level
- **JSON Storage**: Ingredients stored as JSON for flexibility
- **Enum Validation**: Difficulty levels enforced as enum
- **URL Validation**: Image URLs validated for proper format

## 📈 **PERFORMANCE OPTIMIZATIONS**

### Indexes
- **users.email**: UNIQUE index for fast email lookups
- **recipes.owner_id**: INDEX for ownership queries
- **cache_entries.cache_key**: UNIQUE index for fast cache lookups
- **cache_entries.expires_at**: INDEX for cleanup operations

### Query Optimization
- **Pagination**: Efficient LIMIT/OFFSET queries
- **Filtering**: Optimized WHERE clauses for search/filter
- **Sorting**: INDEX support for ORDER BY operations
- **Joins**: Optimized relationship queries

## 🔒 **SECURITY FEATURES**

### Data Protection
- **Password Hashing**: bcrypt with salt rounds
- **Input Validation**: Pydantic schemas with comprehensive validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **Data Sanitization**: Input sanitization at all levels

### Access Control
- **Ownership Validation**: Database-level ownership checks
- **Multi-tenancy**: Secure read/write access patterns
- **Error Handling**: No information leakage in error responses

## 🧪 **TESTING STRATEGY**

### Database Testing
- **SQLite In-memory**: Fast, isolated test database
- **Test Fixtures**: Consistent test data setup
- **Migration Testing**: Alembic migration validation
- **Constraint Testing**: Database constraint validation

### Data Integrity
- **Foreign Key Constraints**: Referential integrity
- **Unique Constraints**: Email uniqueness enforcement
- **Check Constraints**: Field value validation
- **Cascade Operations**: Proper cleanup on deletions

## 📊 **SCHEMA EVOLUTION**

### Migration Management
- **Alembic Migrations**: Version-controlled schema changes
- **Backward Compatibility**: Safe schema updates
- **Data Migration**: Preserve data during schema changes
- **Rollback Support**: Ability to revert schema changes

### Current Migrations
- **Initial Schema**: Users and recipes tables
- **Cache System**: Added cache_entries table
- **Indexes**: Performance optimization indexes
- **Constraints**: Data integrity constraints

## 🏗️ **ARCHITECTURE BENEFITS**

### Scalability
- **Horizontal Scaling**: Stateless design supports multiple instances
- **Database Separation**: Different databases for different environments
- **Caching**: Reduces database load for frequently accessed data
- **Pagination**: Efficient handling of large datasets

### Maintainability
- **Clean Schema**: Well-structured, normalized design
- **Documentation**: Comprehensive schema documentation
- **Type Safety**: SQLAlchemy models with type hints
- **Validation**: Multi-layer validation (database + application)

### Performance
- **Optimized Queries**: Efficient database operations
- **Caching Strategy**: Database-backed caching for performance
- **Index Strategy**: Strategic indexes for common queries
- **Connection Pooling**: Efficient database connection management

This database schema provides a robust, scalable, and maintainable foundation for the Recipe Manager application with enterprise-grade features and excellent performance characteristics.
