# Project Setup Guide

This guide walks through setting up the **Recipe Manager Application** locally. It ensures every developer follows the same environment and conventions.

---

## 1. Clone the Repository

```
git clone git@github.com:your-org/recipe_manager.git
cd recipe_manager
```
## 2. Create Virtual Environment

Use Python 3.10+:
```
python3 -m venv venv
source venv/bin/activate
```
## 3. Install Dependencies
Base dependencies
```
pip install -r requirements/requirements.txt
```
Development dependencies
```
pip install -r requirements/dev_requirements.txt
```

## 4. Environment Configuration

Create a .env file in the project root:

An `.env.example` is provided for reference.

## 5. Database Setup

Ensure PostgreSQL is installed and running locally.

Create the database:
```
psql -U postgres -c "CREATE DATABASE recipe_db;"
```

Run Alembic migrations:
```
alembic upgrade head
```
## 6. Run the Application

Start the Flask app with auto-reload:
```
flask --app src/api/app run --reload
```

**It will be available at:**
```
http://127.0.0.1:5000
```

## 7. Verify Health Endpoint

Check the health API to confirm setup:
```
curl http://127.0.0.1:5000/health
```

**Expected response**:
```
{ "status": "ok" }
```

## 8. Testing

Run the full test suite with coverage:
```
pytest --cov=src
```
## 9. Code Quality

We enforce formatting and linting via pre-commit hooks.

Install hooks:
```
pre-commit install
```

Run manually (optional):
```
pre-commit run --all-files
```

This ensures consistent formatting (Black), linting (Flake8), and basic hygiene checks.
