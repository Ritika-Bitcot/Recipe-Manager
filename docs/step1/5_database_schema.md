# 5. Database Schema Design

## Tables

### users
| Column        | Type      | Constraints       |
|---------------|-----------|-------------------|
| id            | SERIAL    | PK                |
| email         | VARCHAR   | Unique, Not Null  |
| password_hash | VARCHAR   | Not Null          |
| created_at    | TIMESTAMP | Default now()     |

### recipes
| Column        | Type      | Constraints                 |
|---------------|-----------|-----------------------------|
| id            | SERIAL    | PK                          |
| title         | VARCHAR   | Not Null                    |
| description   | TEXT      | Optional                    |
| category      | VARCHAR   | Optional                    |
| instructions  | TEXT      | Not Null                    |
| image_url     | VARCHAR   | Optional                    |
| owner_id      | INT       | FK → users(id), Not Null    |
| created_at    | TIMESTAMP | Default now()               |

### ingredients
| Column        | Type      | Constraints                 |
|---------------|-----------|-----------------------------|
| id            | SERIAL    | PK                          |
| name          | VARCHAR   | Not Null, Unique            |
| quantity      | VARCHAR   | Optional                    |
| recipe_id     | INT       | FK → recipes(id), Not Null  |
| created_at    | TIMESTAMP | Default now()               |

### Relationships
- **Users → Recipes:** 1:N (one user can have multiple recipes)
- **Recipes → Ingredients:** 1:N (one recipe can have multiple ingredients)
