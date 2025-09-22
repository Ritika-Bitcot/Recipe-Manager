# 6. System Architecture

## Authentication Workflow
1. User registers via `/auth/register`.
2. Password is hashed with Bcrypt and stored.
3. User logs in via `/auth/login`.
4. JWT token issued containing user ID & expiry.
5. Token required for recipe endpoints.

![Authentication Diagram](/docs/assets/authentication.png)


## Recipe CRUD Workflow
- **Create:** Authenticated user submits recipe data with ingredients → stored in DB → linked to user and recipe.
- **Read:** User fetches own recipes along with their ingredients via `/recipes` or `/recipes/{id}`.
- **Update:** Only owner can modify recipe fields and associated ingredients.
- **Delete:** Only owner can delete recipe and cascade delete ingredients.

![CRUD Workflow Diagram](/docs/assets/curd_workflow.png)

## ER Diagram
- **Users → Recipes → Ingredients** (1:N → 1:N)
- User (id, email, password_hash, created_at)
- Recipe (id, title, description, category, instructions, image_url, owner_id, created_at)
- Ingredient (id, name, quantity, recipe_id, created_at)

![ER Diagram](/docs/assets/er_diagram.png)

## Security Highlights
- JWT Authentication enforced.
- Passwords stored using Bcrypt hashing.
- Users can only access their own recipes.
- Ingredients are linked to recipes and inherit ownership control.
