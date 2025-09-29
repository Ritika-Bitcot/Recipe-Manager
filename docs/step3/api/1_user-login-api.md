# User Login API

## Endpoint
- **POST** `/auth/login`
- **Authentication Required**: No

---

## Purpose
Authenticate a registered user and return a JWT token.

---

## Request Body
- **email**: string (required, valid email format)
- **password**: string (required, minimum 8 characters)

---

## Response
- **200 OK** on success:
```
  {
    "access_token": "jwt_token_string",
    "token_type": "bearer"
  }
```

## Errors:

**401 Unauthorized** → invalid credentials

**422 Unprocessable** → missing or invalid fields

## Validations

- Email must be in valid format.

- Password minimum length: 8 chars.

- JWT is issued only on valid credentials.