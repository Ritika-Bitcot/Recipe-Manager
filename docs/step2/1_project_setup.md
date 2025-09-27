# Project Setup Guide

This guide walks through setting up the **Recipe Manager Application** locally. It ensures every developer follows the same environment and conventions with enterprise-grade features.

---

## ✅ **QUICK START**

### Prerequisites
- Python 3.10+
- PostgreSQL 12+ (for development)
- Git
- Virtual environment (venv, conda, or pipenv)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Recipe-Manager
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Production dependencies
pip install -r requirements/requirements.txt

# Development dependencies (optional)
pip install -r requirements/dev_requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 5. Database Setup
```bash
# Ensure PostgreSQL is running
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database
psql -U postgres -c "CREATE DATABASE recipe_manager;"

# Run migrations
alembic upgrade head
```

### 6. Run the Application
```bash
# Start the Flask app
python -m src.api.app

# Or with auto-reload for development
flask --app src.api.app run --reload
```

**Application will be available at:**
```
http://localhost:5000
```

### 7. Verify Setup
```bash
# Check health endpoint
curl http://localhost:5000/health

# Check API status
curl http://localhost:5000/
```

**Expected responses:**
```json
// Health check
{ "status": "ok" }

// API status
{ "message": "Recipe Manager API", "version": "1.0.0", "status": "running" }
```

## 🧪 **TESTING SETUP**

### Run Test Suite
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_services.py

# Run with verbose output
pytest -v
```

### Test Database
- **Testing**: SQLite in-memory database (automatic)
- **Isolation**: Each test runs in a clean database state
- **Fixtures**: Reusable test data and database sessions

## 🔧 **CODE QUALITY**

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Run on specific files
pre-commit run --files src/api/routes/recipe_routes.py
```

### Code Formatting
```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/
```

## 🚀 **ADVANCED FEATURES**

### Caching System
The application includes a SQLAlchemy-based caching system:
- **Database-backed**: Uses `cache_entries` table
- **Automatic Invalidation**: Cache cleared on data changes
- **Configurable TTL**: Time-to-live for cache entries
- **Pattern-based Deletion**: Bulk cache invalidation

### Multi-tenancy
- **Read Access**: Users can read all recipes
- **Write Access**: Users can only modify their own recipes
- **Security**: Comprehensive ownership validation

### Environment Configuration
```bash
# Development
ENVIRONMENT=development
DATABASE_URL=postgresql://user:pass@localhost:5432/recipe_manager_dev
LOG_LEVEL=DEBUG
ENABLE_CACHE=true

# Testing
ENVIRONMENT=testing
DATABASE_URL=sqlite:///test.db
LOG_LEVEL=WARNING
ENABLE_CACHE=false

# Production
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/recipe_manager_prod
LOG_LEVEL=INFO
ENABLE_CACHE=true
```

## 📊 **DEVELOPMENT WORKFLOW**

### 1. Make Changes
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make your changes
# ... edit files ...

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Commit changes
git add .
git commit -m "Add new feature"
```

### 2. Database Changes
```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### 3. Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test
pytest tests/test_services.py::TestRecipeService::test_create_recipe_success
```

## 🔍 **TROUBLESHOOTING**

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
psql -U postgres -l

# Test connection
psql -U postgres -d recipe_manager -c "SELECT 1;"
```

#### Import Issues
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install in development mode
pip install -e .

# Check virtual environment
which python
```

#### Test Issues
```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -v -s

# Run specific test with debug
pytest tests/test_services.py::TestRecipeService::test_create_recipe_success -v -s
```

### Environment Variables
```bash
# Check environment variables
env | grep DATABASE_URL
env | grep SECRET_KEY

# Load environment file
source .env
```

## 📚 **NEXT STEPS**

### 1. Explore the API
```bash
# Register a user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123!"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123!"}'

# Create a recipe (use token from login)
curl -X POST http://localhost:5000/api/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title": "Test Recipe", "instructions": "Test instructions"}'
```

### 2. Run Tests
```bash
# Full test suite
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 3. Explore Documentation
- **README.md**: Complete project overview
- **docs/API_OVERVIEW.md**: Detailed API documentation
- **docs/ARCHITECTURE.md**: System architecture
- **docs/TESTING.md**: Testing documentation
- **docs/DEPLOYMENT.md**: Deployment guide

## 🎯 **SUCCESS CRITERIA**

Your setup is successful when:
- ✅ Application starts without errors
- ✅ Health endpoint returns `{"status": "ok"}`
- ✅ All tests pass (`pytest`)
- ✅ Pre-commit hooks run successfully
- ✅ Database migrations apply without errors
- ✅ API endpoints respond correctly

This setup provides a robust development environment with enterprise-grade features, comprehensive testing, and excellent developer experience!