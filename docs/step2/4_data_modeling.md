# Data Modeling Guide

This guide explains the **data modeling** approach for the Recipe Manager Application using **Flask + SQLAlchemy + Alembic** with enterprise-grade features including multi-tenancy, caching, and comprehensive testing.

---

## ✅ **IMPLEMENTED DATA MODELING**

### 1. Database Architecture

#### Multi-Environment Database Strategy
- **Development**: PostgreSQL (ACID-compliant, production-ready)
- **Testing**: SQLite in-memory (fast, isolated testing)
- **Production**: PostgreSQL with connection pooling
- **Caching**: Database-backed caching system

#### Database Choice Rationale
- **PostgreSQL**: Primary database for development and production
  - ACID compliance ensures data integrity
  - JSONB support for flexible ingredient storage
  - Strong community support and reliability
  - Advanced indexing and query optimization
- **SQLite**: Testing database
  - In-memory for fast test execution
  - Automatic cleanup after tests
  - No external dependencies for testing

---

## 2. ORM: SQLAlchemy Implementation

### Advanced SQLAlchemy Features
- **Pythonic abstraction** over SQL with full type safety
- **Relationship management** with proper foreign key constraints
- **Migration support** via Alembic for schema versioning
- **Query optimization** with strategic indexing
- **Connection pooling** for production performance

### Architecture Pattern
- **Repository Pattern**: Data access abstraction layer
- **Service Layer**: Business logic encapsulation
- **Interface Segregation**: Focused contract design
- **Dependency Injection**: Loose coupling between components

---

## 3. Implemented Models & Relationships

### 3.1 User Model (`src/models/user_model.py`)
```python
class User(db.Model):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    recipes = relationship("Recipe", back_populates="owner", cascade="all, delete-orphan")
```

**Features:**
- Unique email constraint with index for performance
- Password hashing with bcrypt
- Account status management
- Automatic timestamp management
- One-to-many relationship with recipes

### 3.2 Recipe Model (`src/models/recipe_model.py`)
```python
class Recipe(db.Model):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    ingredients = Column(JSON, nullable=True)  # JSON array for flexibility
    instructions = Column(Text, nullable=False)
    prep_time = Column(Integer, nullable=True)  # minutes
    cook_time = Column(Integer, nullable=True)  # minutes
    servings = Column(Integer, nullable=True)
    cuisine = Column(String(50), nullable=True)
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    image_url = Column(String(500), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="recipes")
```

**Features:**
- Comprehensive recipe metadata
- JSON storage for flexible ingredients
- Foreign key relationship with users
- Indexed owner_id for query performance
- Automatic timestamp management

### 3.3 Cache Model (`src/models/cache_model.py`)
```python
class CacheEntry(db.Model):
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    cache_value = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**Features:**
- Database-backed caching system
- Unique cache keys with indexing
- TTL management with expiration timestamps
- JSON serialization for complex data types

---

## 4. Database Migrations: Alembic

### Migration Management
- **Version Control**: Complete schema versioning
- **Safe Updates**: Backward-compatible schema changes
- **Data Preservation**: Maintain data integrity during migrations
- **Rollback Support**: Ability to revert schema changes

### Current Migrations
- **Initial Schema**: Users and recipes tables
- **Cache System**: Added cache_entries table
- **Indexes**: Performance optimization indexes
- **Constraints**: Data integrity constraints

### Migration Commands
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current status
alembic current
```

---

## 5. Relationships & Constraints

### Primary Relationships
- **Users → Recipes**: 1:N (one user can have multiple recipes)
- **Cache Entries**: Independent table for caching system

### Foreign Key Constraints
- **recipes.owner_id** → **users.id** (CASCADE on user deletion)
- **Indexes**: Optimized for query performance

### Data Integrity
- **Unique Constraints**: Email uniqueness enforcement
- **Check Constraints**: Field value validation
- **Cascade Operations**: Proper cleanup on deletions
- **Referential Integrity**: Foreign key constraints

---

## 6. Advanced Features

### Multi-tenancy Implementation
- **Read Access**: Users can read all recipes via `GET /api/recipes`
- **Write Access**: Users can only modify their own recipes
- **Ownership Validation**: Enforced at service layer and database level
- **Security**: Comprehensive ownership checks for all write operations

### Caching System
- **Database-backed Caching**: Uses `cache_entries` table
- **Automatic Invalidation**: Cache cleared on data changes
- **TTL Management**: Configurable time-to-live for cache entries
- **Pattern-based Deletion**: Bulk cache invalidation capabilities

### Performance Optimizations
- **Strategic Indexing**: Optimized for common query patterns
- **Query Optimization**: Efficient database operations
- **Connection Pooling**: Efficient database connection management
- **Pagination**: Efficient handling of large datasets

---

## 7. Data Validation

### Multi-layer Validation
- **Database Level**: Field constraints and data types
- **Application Level**: Pydantic schemas with comprehensive validation
- **Service Level**: Business logic validation
- **API Level**: Request/response validation

### Validation Features
- **Field Constraints**: Comprehensive validation at database level
- **JSON Storage**: Ingredients stored as JSON for flexibility
- **Enum Validation**: Difficulty levels enforced as enum
- **URL Validation**: Image URLs validated for proper format
- **Type Safety**: Full type hints and Pydantic validation

---

## 8. Testing Strategy

### Database Testing
- **SQLite In-memory**: Fast, isolated test database
- **Test Fixtures**: Consistent test data setup
- **Migration Testing**: Alembic migration validation
- **Constraint Testing**: Database constraint validation

### Test Coverage
- **Model Tests**: Comprehensive model validation
- **Relationship Tests**: Foreign key and relationship testing
- **Migration Tests**: Schema change validation
- **Performance Tests**: Query optimization testing

---

## 9. SOLID Principles Applied

### Single Responsibility
- **User Model**: Manages user data and authentication
- **Recipe Model**: Manages recipe data and metadata
- **Cache Model**: Manages caching data and TTL

### Open/Closed
- **Extensible Models**: Can be extended without modification
- **Interface-based**: Repository interfaces for data access
- **Plugin Architecture**: Easy to add new model types

### Liskov Substitution
- **Polymorphic Queries**: Repository interfaces support polymorphic operations
- **Consistent Interfaces**: All models follow same patterns
- **Substitutable Implementations**: Different database backends

### Interface Segregation
- **Repository Interfaces**: Focused data access contracts
- **Service Interfaces**: Business logic contracts
- **Model Interfaces**: Entity contracts

### Dependency Inversion
- **Repository Pattern**: Services depend on interfaces
- **Service Layer**: Business logic depends on abstractions
- **Database Abstraction**: ORM provides database abstraction

---

## 10. Best Practices Implemented

### Model Design
- **Lightweight Models**: Only database columns and relationships
- **Clear Naming**: Descriptive table and column names
- **Proper Indexing**: Strategic indexes for performance
- **Relationship Management**: Proper foreign key relationships

### Validation Strategy
- **Multi-layer Validation**: Database, application, and API levels
- **Type Safety**: Full type hints throughout
- **Error Handling**: Comprehensive error responses
- **Data Sanitization**: Input sanitization at all levels

### Performance Considerations
- **Query Optimization**: Efficient database queries
- **Index Strategy**: Strategic indexes for common queries
- **Connection Management**: Efficient database connections
- **Caching Strategy**: Database-backed caching for performance

---

## 11. Summary

The Recipe Manager data modeling provides a **robust, scalable, and maintainable database layer** with:

- **PostgreSQL + SQLAlchemy + Alembic**: Reliable, scalable database foundation
- **Multi-tenancy**: Secure read/write access patterns
- **Caching System**: Database-backed caching for performance
- **Comprehensive Testing**: SQLite in-memory for fast testing
- **SOLID Principles**: Clean architecture with proper abstractions
- **Performance Optimization**: Strategic indexing and query optimization
- **Data Integrity**: Comprehensive validation and constraint enforcement

This data modeling approach ensures the Recipe Manager application has enterprise-grade database capabilities with excellent performance, security, and maintainability!