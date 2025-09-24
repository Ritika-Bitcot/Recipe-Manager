# GitHub Workflows

This document describes how **GitHub Actions** and our **stepwise branching workflow** are used to manage the Recipe Manager Application repository.

---

## 1. Branching Strategy

We use a **modified GitHub Flow** with step-based branches:

1. **main**
   - Stable, production-ready branch.
   - Contains only thoroughly tested and reviewed code.
   - Protected: requires PR approval + CI checks.

2. **develop**
   - Integration branch for ongoing development.
   - All stepwise feature branches merge here first.
   - Serves as a staging ground before merging into `main`.

3. **feat/stepX**
   - Short-lived branches for features or documentation aligned with project steps.
   - Example:  
     - `feat/step1` → Planning & requirements  
     - `feat/step2` → Implementation guides  
     - `feat/step3` → API implementation  
     - `feat/step4` → Testing & best practices  

### Workflow of Branches
- Work starts in **`feat/stepX`**.  
- Open PR into **`develop`** once complete.  
- After review & CI checks, merge into **`develop`**.  
- When a full milestone is stable, merge **`develop` → `main`**.  

This enforces **structured progression** of the project.

---

## 2. Continuous Integration (CI)

CI runs automatically on **every commit and pull request** to `develop` and `main`.

### Workflow Tasks
1. **Setup Python Environment**
   - Install dependencies from `requirements.txt`.

2. **Code Quality**
   - Run `flake8` for linting.
   - Run `black --check` for formatting.

3. **Testing**
   - Run `pytest` with coverage.
   - Use PostgreSQL service for DB tests.

4. **Database Migrations**
   - Validate Alembic migrations (`alembic upgrade head`).