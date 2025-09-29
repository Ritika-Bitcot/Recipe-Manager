# Recipe Manager API

A comprehensive RESTful API for managing recipes with user authentication, multi-tenancy, and advanced caching capabilities.

## 🚀 Features

### Core Functionality
- **User Authentication**: JWT-based authentication with secure password hashing
- **Recipe Management**: Full CRUD operations for recipes
- **Multi-tenancy**: Users can only modify their own recipes but can read all recipes
- **Advanced Caching**: SQLAlchemy-based caching system for improved performance
- **Input Validation**: Comprehensive validation using Pydantic schemas
- **Error Handling**: Centralized error handling with detailed error responses

### Technical Features
- **Clean Architecture**: Layered architecture following SOLID principles
- **Type Safety**: Full type hints and Pydantic validation
- **Async Support**: High-performance async operations
- **Database Separation**: Separate databases for development and testing
- **Comprehensive Testing**: 82% test coverage with 359 tests
- **Code Quality**: Automated linting and formatting with pre-commit hooks

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL (for development)
- SQLite (for testing)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Recipe-Manager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

## 🚀 Quick Start

1. **Start the application**
   ```bash
   python -m src.api.app
   ```

2. **Register a new user**
   ```bash
   curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "SecurePass123!"}'
   ```

3. **Login and get token**
   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "SecurePass123!"}'
   ```

4. **Create a recipe**
   ```bash
   curl -X POST http://localhost:5000/api/recipes \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "title": "Chocolate Cake",
       "description": "Delicious chocolate cake recipe",
       "ingredients": ["flour", "sugar", "cocoa", "eggs"],
       "instructions": "Mix ingredients and bake",
       "prep_time": 30,
       "cook_time": 45,
       "servings": 8,
       "cuisine": "American",
       "difficulty": "medium"
     }'
   ```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |
| POST | `/api/auth/logout` | Logout (token blacklisting) |
| GET | `/api/auth/me` | Get current user profile |

### Recipe Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recipes` | Get all recipes (with pagination) |
| GET | `/api/recipes/{id}` | Get recipe by ID |
| POST | `/api/recipes` | Create new recipe |
| PUT | `/api/recipes/{id}` | Update recipe (owner only) |
| DELETE | `/api/recipes/{id}` | Delete recipe (owner only) |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/ready` | Readiness check with database |

## 🏗️ Architecture

### Project Structure
```
src/
├── api/                    # API layer
│   ├── routes/            # Route handlers
│   └── app.py             # Flask application factory
├── core/                  # Core functionality
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection
│   ├── error_handler.py   # Error handling
│   └── exceptions.py      # Custom exceptions
├── interfaces/            # Interface definitions
│   ├── repository/        # Repository interfaces
│   └── service/           # Service interfaces
├── models/                # SQLAlchemy models
├── repositories/          # Data access layer
├── schemas/               # Pydantic schemas
├── services/              # Business logic layer
│   ├── authentication/    # Auth services
│   ├── caching/           # Caching services
│   └── recipe_management/ # Recipe services
├── utils/                 # Utility functions
└── validators/            # Input validators
```

### Design Patterns

- **Repository Pattern**: Data access abstraction
- **Service Layer Pattern**: Business logic encapsulation
- **Interface Segregation**: Focused contract design
- **Dependency Injection**: Loose coupling between components

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["*"]` |
| `ENVIRONMENT` | Environment (dev/test/prod) | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CACHE_TTL` | Cache time-to-live (seconds) | `300` |
| `ENABLE_CACHE` | Enable caching | `True` |

### Database Configuration

- **Development**: PostgreSQL
- **Testing**: SQLite in-memory
- **Migrations**: Alembic for schema management

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_services.py
```

### Test Coverage
- **Overall Coverage**: 82%
- **Total Tests**: 359
- **Test Categories**:
  - Unit tests for services and utilities
  - Integration tests for API endpoints
  - Repository pattern tests
  - Caching system tests
  - Authentication and authorization tests

## 🚀 Performance Features

### Caching System
- **SQLAlchemy-based caching**: Database-backed cache storage
- **Automatic invalidation**: Cache invalidation on data changes
- **Configurable TTL**: Time-to-live for cache entries
- **Pattern-based deletion**: Bulk cache invalidation

### Multi-tenancy
- **Read Access**: Users can read all recipes
- **Write Access**: Users can only modify their own recipes
- **Security**: Authorization checks on all write operations

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Input Validation**: Comprehensive validation using Pydantic
- **CORS Support**: Configurable cross-origin resource sharing
- **Error Handling**: Secure error responses without information leakage

## 📊 Monitoring & Logging

- **Structured Logging**: JSON-formatted logs
- **Log Levels**: Configurable logging levels
- **Request Tracking**: Comprehensive request/response logging
- **Error Tracking**: Detailed error logging and reporting

## 🛠️ Development

### Code Quality
- **Pre-commit Hooks**: Automated code formatting and linting
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checking

### Running Pre-commit
```bash
pre-commit run --all-files
```

## 📈 API Usage Examples

### Complete Workflow Example

1. **Register User**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "chef@example.com",
    "password": "MySecurePassword123!"
  }'
```

2. **Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "chef@example.com",
    "password": "MySecurePassword123!"
  }'
```

3. **Create Recipe**
```bash
curl -X POST http://localhost:5000/api/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Spaghetti Carbonara",
    "description": "Classic Italian pasta dish",
    "ingredients": ["spaghetti", "eggs", "pancetta", "parmesan", "black pepper"],
    "instructions": "1. Cook pasta 2. Fry pancetta 3. Mix with eggs and cheese",
    "prep_time": 15,
    "cook_time": 20,
    "servings": 4,
    "cuisine": "Italian",
    "difficulty": "medium"
  }'
```

4. **Get All Recipes**
```bash
curl -X GET "http://localhost:5000/api/recipes?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and pre-commit hooks
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository.
