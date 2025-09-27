# User Registration API

## Endpoint
- **POST** `/auth/register`
- **Authentication Required**: No

---

## Purpose
Allows a new user to register with email and password.

---

## Request Body
- **email**: string (required, valid email format)
- **password**: string (required, minimum 8 characters, 1 uppercase, 1 lowercase, 1 number)

---

## Response
- **201 Created** on success:
  ```json
  {
    "message": "User registered successfully"
  }

## Errors:

**400 Bad Request** → email already exists

**422 Unprocessable** → invalid email or password format

## Validations

- Email must be unique.

- Password must meet complexity rules.

- Email format validated using regex.

- Password hashed using Bcrypt before storing.