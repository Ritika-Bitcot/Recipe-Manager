# Data Modeling Guide
This guide explains the **data modeling** approach for the Recipe Manager Application using **Flask + SQLAlchemy + Alembic**.

---

## 1. Database Choice

- **PostgreSQL** is used as the relational database.
- Reasons:
  - ACID compliance ensures data integrity.
  - JSONB support for flexible ingredient storage.
  - Strong community support and reliability.

---

## 2. ORM: SQLAlchemy

- Provides **Pythonic abstraction** over SQL.
- Benefits:
  - Reduces manual SQL writing.
  - Easy relationships management.
  - Supports migrations via Alembic.
- Pattern used:
  - **Repositories + Services + Interfaces** (SOLID-aligned)
  - All models are **entities** used by repositories.

---

## 3. Models & Relationships

### 3.1 User Model
- Represents the user entity.
- Each user can have **multiple recipes** (1:N).
- Stores unique email, hashed password, and creation timestamp.

### 3.2 Recipe Model
- Represents the recipe entity.
- Linked to the owner user to enforce **access control**.
- Stores title, description, category, ingredients (JSONB), instructions, image, and timestamps.

### 3.3 Ingredient Model (Optional)
- Can be used as a separate normalized table if detailed ingredient queries are required.
- Linked to recipes (1:N).

---

## 4. Database Migrations: Alembic

- Migrations allow **version control of database schema**.
- Key practices:
  - Keep migrations in `migrations/` folder.
  - Always generate migrations when schema changes.
  - Apply migrations consistently across development and testing environments.

---

## 5. Relationships Diagram (ERD)

- User 1:N Recipe
- Recipe 1:N Ingredient (optional)
- Diagram is stored in `docs/assets/erd.png`.

---

## 6. Best Practices

1. Keep models **lightweight**, only including DB columns and relationships.
2. **Validation** should be handled at schema level (Pydantic) or service layer.
3. **Repositories** interact directly with models; services use repositories.
4. Avoid **circular dependencies** by using interfaces.

---

## 7. SOLID Alignment

- **S**: Single Responsibility → each model represents **one table/entity**.
- **O**: Open/Closed → models can be extended without modification.
- **L**: Liskov → relationships support polymorphic queries.
- **I**: Interface Segregation → repository interfaces ensure separation.
- **D**: Dependency Inversion → services depend on interfaces, not concrete models.

---

## 8. Summary

- PostgreSQL + SQLAlchemy + Alembic provides a **reliable, scalable, maintainable database layer**.
- Models enforce **ownership and relationships**.
- Repository pattern + interfaces ensures **clean architecture** aligned with **SOLID principles**.