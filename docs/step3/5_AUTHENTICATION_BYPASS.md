# Authentication Bypass for Development

This document explains how to use the authentication bypass feature for development purposes.

## Overview

The authentication bypass feature allows developers to skip JWT token validation during development by configuring a specific email address. This is useful for:

- Testing API endpoints without generating JWT tokens
- Development and debugging
- Automated testing scenarios

## Configuration

### Environment Variable

Set the `AUTH_BYPASS_EMAIL` environment variable to enable bypass:

```bash
# In your .env file or environment
AUTH_BYPASS_EMAIL=dev@example.com
```

### Example .env Configuration

```env
# Authentication Bypass for Development
# Set to a valid email address to bypass authentication during development
# Leave empty, unset, or set to None/null to use normal JWT authentication
AUTH_BYPASS_EMAIL=dev@example.com
```

### Development vs Production Behavior

**Development Mode:**
```env
AUTH_BYPASS_EMAIL=developer@example.com
```
- ✅ Authentication bypass is **enabled**
- ✅ No JWT token required for protected endpoints
- ✅ User is automatically authenticated using the specified email

**Production Mode:**
```env
# Any of these configurations will disable bypass:
AUTH_BYPASS_EMAIL=
AUTH_BYPASS_EMAIL=None
AUTH_BYPASS_EMAIL=null
# Or simply don't set the variable at all
```
- ❌ Authentication bypass is **disabled**
- ✅ Normal JWT authentication is required
- ✅ All protected endpoints require valid Authorization header

## How It Works

1. **Bypass Check**: When a protected endpoint is accessed, the system first checks if `AUTH_BYPASS_EMAIL` is configured
2. **User Lookup**: If bypass is enabled, the system looks up the user by the configured email address
3. **Authentication**: The user is automatically authenticated without requiring a JWT token
4. **Normal Flow**: If bypass is disabled, normal JWT authentication is used

## Usage

### With Bypass Enabled

```bash
# No Authorization header needed
curl -X GET http://localhost:5000/api/recipes
```

### With Bypass Disabled (Normal Authentication)

```bash
# Requires valid JWT token
curl -X GET http://localhost:5000/api/recipes \
  -H "Authorization: Bearer your-jwt-token-here"
```

## Implementation Details

### New Decorator

The system introduces a new `@auth_required` decorator that replaces `@jwt_required()`:

```python
from src.utils.auth_decorators import auth_required

@recipe_bp.route("/recipes", methods=["GET"])
@auth_required
def get_recipes():
    user_id = g.current_user_id  # Available in Flask's g object
    user_email = g.current_user_email  # Available in Flask's g object
    # ... rest of the function
```

### User Information Access

When using the bypass, user information is available in Flask's `g` object:

- `g.current_user_id`: The user's ID
- `g.current_user_email`: The user's email address

## Security Considerations

⚠️ **Important Security Notes:**

1. **Development Only**: This feature should only be used in development environments
2. **Never in Production**: Never set `AUTH_BYPASS_EMAIL` in production
3. **Valid User Required**: The bypass email must correspond to an existing user in the database
4. **Environment Separation**: Use different environment configurations for development and production

## Troubleshooting

### Common Issues

1. **Bypass User Not Found**
   ```
   Error: Bypass user not found: dev@example.com
   ```
   **Solution**: Ensure the email address exists in the user database

2. **Database Connection Issues**
   ```
   Error: Bypass authentication failed: [database error]
   ```
   **Solution**: Check database connectivity and user table

3. **Configuration Not Loaded**
   ```
   Error: Invalid authentication credentials
   ```
   **Solution**: Verify `AUTH_BYPASS_EMAIL` is properly set in environment

### Debugging

Enable debug logging to see bypass activity:

```python
import logging
logging.getLogger('src.utils.auth_decorators').setLevel(logging.DEBUG)
```

## Migration from JWT-Only

To migrate existing routes from JWT-only to bypass-enabled:

1. **Replace Decorator**:
   ```python
   # Before
   @jwt_required()
   
   # After
   @auth_required
   ```

2. **Update User ID Access**:
   ```python
   # Before
   user_id = int(get_jwt_identity())
   
   # After
   user_id = g.current_user_id
   ```

3. **Add Import**:
   ```python
   from src.utils.auth_decorators import auth_required
   from flask import g
   ```

## Testing

Use the provided test script to verify bypass functionality:

```bash
python test_auth_bypass.py
```

This will test both bypass-enabled and normal authentication modes.
