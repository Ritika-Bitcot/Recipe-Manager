# 3. User Stories with Acceptance Criteria

## 1. User Registration
**Story:** As a new user, I want to register with a unique email and password to securely manage recipes.  
**Acceptance Criteria:**
- ✅ Validate email format.
- ✅ Enforce strong password policy (min 8 chars, 1 uppercase, 1 lowercase, 1 number).
- ✅ Reject if email already exists.
- ✅ Store password securely with Bcrypt.
- ✅ Return 201 Created with success message.

## 2. User Login
**Story:** As a registered user, I want to log in with credentials and receive a JWT token.  
**Acceptance Criteria:**
- ✅ Validate credentials.
- ✅ Return 401 Unauthorized for invalid login.
- ✅ Return 200 OK with JWT token on success.
- ✅ JWT contains user ID and expiry.

## 3. Create Recipe
**Story:** As a logged-in user, I want to create recipes with ingredients and instructions.  
**Acceptance Criteria:**
- ✅ Authenticated users only.
- ✅ Recipe requires title & instructions.
- ✅ Optional: description, category, image.
- ✅ Linked to logged-in user.
- ✅ Return 201 Created with recipe details.

## 4. View Recipes
**Story:** As a logged-in user, I want to view my recipes and search them by title or category.  
**Acceptance Criteria:**
- ✅ Authenticated users only.
- ✅ Only own recipes visible.
- ✅ GET /recipes → all recipes for user.
- ✅ GET /recipes/{id} → single recipe if owned.
- ✅ Return 403 Forbidden if accessing others’ recipes.
- ✅ Return 404 Not Found if recipe doesn’t exist.

## 5. Update Recipe
**Story:** As a logged-in user, I want to update my recipes.  
**Acceptance Criteria:**
- ✅ Authenticated users only.
- ✅ Update own recipes only.
- ✅ Allowed updates: title, description, category, ingredients, instructions, image.
- ✅ Reject invalid formats.
- ✅ Return 200 OK with updated recipe.
- ✅ Return 403 Forbidden if not owner.

## 6. Delete Recipe
**Story:** As a logged-in user, I want to delete recipes I no longer need.  
**Acceptance Criteria:**
- ✅ Authenticated users only.
- ✅ Delete own recipes only.
- ✅ Return 200 OK with confirmation.
- ✅ Return 403 Forbidden if not owner.
- ✅ Return 404 Not Found if recipe doesn’t exist.
