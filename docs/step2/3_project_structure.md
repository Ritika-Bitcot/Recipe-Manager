# Project Structure

This document defines the **Recipe Manager Application** project structure.  
Each folder and file is annotated with its purpose to ensure clarity, maintainability, and scalability.

---

## Root Directory

```
recipe_manager/
├── migrations/ # Alembic migrations (DB versioning)
│
├── docs/ # Documentation and diagrams
│ ├── assets/ # Visual diagrams
│ │ ├── er_diagram.png # ER diagram
│ │ ├── crud_workflow.png # CRUD API flow diagram
│ │ └── authentication.png # Auth flow diagram
│
├── step1/ # Planning & requirements docs
│ ├── 1_planning.md # Project overview
│ ├── 2_design.md # Tech stack & design decisions
│ ├── 3_user_stories.md # User requirements
│ ├── 4_api_end_points_overview.md # API specifications
│ ├── 5_database_schema.md # Schema & ERD
│ └── 6_architecture.md # Architecture diagrams
│
├── step2/ # Implementation guides
│ ├── 1_project_setup.md # Repo setup guide
│ ├── 2_github_flow.md # GitHub workflow (branching strategy)
│ ├── 3_project_structure.md # This document
│ └── 4_data_modeling.md # SQLAlchemy + Alembic modeling
│
├── step3/ # API implementation docs
│ ├── 1_user-login-api.md # Guide: Login API
│ └── 2_user-registration.md # Guide: Register API
│ ├── 3_create-recipe.md # Guide: Create recipe API
│ ├── 4_get-all-recipes.md # Guide: List recipes API
│ ├── 5_get-recipe-by-id.md # Guide: Get recipe by ID API
│ ├── 6_delete-recipe.md # Guide: Delete recipe API
│ ├── 7_update-recipe.md # Guide: Update recipe API
│
├── step4/ # Testing & best practices
│ ├── api_testing_guide.md # Testing API endpoints
│ ├── local_setup_and_testing.md # Local dev setup
│ ├── postman_testing_guide.md # Postman usage
│ ├── project_structure.md # Final structure summary
│ └── solid_principles.md # SOLID principles applied
│
├── requirements/ # Dependency management
│ ├── requirements.txt # Prod dependencies
│ └── dev_requirements.txt # Dev/test dependencies
│
├── src/ # Application source code
│ ├── api/ # Flask application layer
│ │ ├── app.py # Flask app factory
│ │ └── routes/ # API routes
│ │ ├── auth_routes.py # Endpoints for register/login
│ │ ├── recipe_routes.py # Endpoints for CRUD recipes
│ │ └── health_routes.py # Health & readiness checks
│ │
│ ├── core/ # Core utilities & configs
│ │ ├── config.py # Env-based settings
│ │ ├── database.py # SQLAlchemy + Alembic setup
│ │ ├── exceptions.py # Custom exceptions
│ │ └── validators.py # Input validators
│ │
│ ├── interfaces/ # Abstract contracts (SOLID)
│ │ ├── repository/ # Repository interfaces
│ │ │ ├── base_repository_interface.py
│ │ │ ├── user_repository_interface.py
│ │ │ └── recipe_repository_interface.py
│ │ └── service/ # Service interfaces
│ │ ├── auth_service_interface.py
│ │ └── recipe_service_interface.py
│ │
│ ├── models/ # SQLAlchemy ORM models
│ │ ├── user_model.py # User table
│ │ ├── recipe_model.py # Recipe table
│ │ └── ingredient_model.py # Optional ingredients table
│ │
│ ├── repositories/ # DB access implementations
│ │ ├── base_repository.py # Common CRUD helpers
│ │ ├── user_repository.py # User DB logic
│ │ └── recipe_repository.py # Recipe DB logic
│ │
│ ├── schemas/ # Pydantic request/response models
│ │ ├── user_schema.py # User validation
│ │ ├── auth_schema.py # Login/Register schemas
│ │ └── recipe_schema.py # Recipe validation
│ │
│ ├── services/ # Business logic layer
│ │ ├── authentication/ # Auth domain
│ │ │ ├── auth_service.py # JWT generation/validation
│ │ │ └── password_service.py # Password hashing
│ │ └── recipe_management/ # Recipe domain
│ │ └── recipe_service.py # Recipe business logic
│ │
│ ├── utils/ # Stateless helpers
│ │ ├── jwt_helper.py # JWT encode/decode helpers
│ │ └── password_helper.py # Bcrypt helpers
│ │
│ └── init.py
│
├── tests/ # Test suite
│ ├── api/ # API endpoint tests
│ │ ├── conftest.py # API fixtures
│ │ ├── test_auth_routes.py # Test /auth endpoints
│ │ └── test_recipe_routes.py # Test /recipes endpoints
│ │
│ ├── integration/ # Integration tests
│ │ ├── test_auth_system.py # End-to-end auth flow
│ │ ├── test_database.py # DB migrations + models
│ │ └── test_recipe_system.py # End-to-end recipe lifecycle
│ │
│ └── unit/ # Unit tests
│ ├── conftest.py # Unit fixtures
│ ├── test_auth_service.py # Test auth service
│ ├── test_password_service.py # Test password service
│ ├── test_recipe_service.py # Test recipe service
│ └── test_models.py # Test ORM models
│
├── .env.example # Example env config
├── alembic.ini # Alembic config file
├── pytest.ini # Pytest config
├── .pre-commit-config.yaml # Pre-commit hooks
├── .flake8 # Flake8 rules
├── README.md # Main project doc
└── CHANGELOG.md # Version history
```

---

## Notes
- This structure is designed to **never require rewriting** as the project grows.  
- Each file/folder has a **clear responsibility** aligned with **SOLID principles**.  

---
