"""Password utility functions for hashing and verification."""

import bcrypt


class PasswordHelper:
    """Password helper class for hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        # Truncate password to 72 bytes (bcrypt limit)
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            # Truncate password to 72 bytes (bcrypt limit) to match hash_password behavior
            password_bytes = password.encode("utf-8")
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]

            return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def is_password_strong(password: str) -> bool:
        """Check if password meets strength requirements."""
        if len(password) < 8:
            return False

        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            return False

        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            return False

        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            return False

        return True
