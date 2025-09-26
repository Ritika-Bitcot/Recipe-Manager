"""Tests for authentication API routes."""

import json
from unittest.mock import patch

from src.core.exceptions import AuthenticationError, ConflictError, ResourceNotFoundError


class TestAuthRoutes:
    """Test authentication route functionality."""

    def test_register_success(self, client, sample_user_data):
        """Test successful user registration."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.register_user.return_value = {
                "user": {"id": 1, "email": sample_user_data["email"]},
                "token": "mock_token",
                "message": "User registered successfully",
            }

            response = client.post("/api/auth/register", json=sample_user_data)

            assert response.status_code == 201
            data = response.get_json()
            assert "user" in data
            assert "token" in data
            assert "message" in data
            assert data["message"] == "User registered successfully"

    def test_register_validation_error(self, client, invalid_user_data):
        """Test user registration with validation error."""
        response = client.post("/api/auth/register", json=invalid_user_data)

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_register_email_exists(self, client, sample_user_data):
        """Test user registration with existing email."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.register_user.side_effect = ConflictError("Email already registered", "email")

            response = client.post("/api/auth/register", json=sample_user_data)

            assert response.status_code == 409
            data = response.get_json()
            assert "error" in data
            assert data["error"] == "CONFLICT_ERROR"

    def test_register_missing_data(self, client):
        """Test user registration with missing required data."""
        response = client.post("/api/auth/register", json={})

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_register_invalid_json(self, client):
        """Test user registration with invalid JSON."""
        response = client.post("/api/auth/register", data="invalid json", content_type="application/json")

        assert response.status_code == 400

    def test_login_success(self, client, sample_user_data):
        """Test successful user login."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.login_user.return_value = {
                "user": {"id": 1, "email": sample_user_data["email"]},
                "token": "mock_token",
                "message": "Login successful",
            }

            login_data = {
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            }
            response = client.post("/api/auth/login", json=login_data)

            assert response.status_code == 200
            data = response.get_json()
            assert "user" in data
            assert "token" in data
            assert "message" in data
            assert data["message"] == "Login successful"

    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.login_user.side_effect = AuthenticationError("Invalid email or password")

            login_data = {
                "email": sample_user_data["email"],
                "password": "wrong_password",
            }
            response = client.post("/api/auth/login", json=login_data)

            assert response.status_code == 401
            data = response.get_json()
            assert "error" in data
            assert data["error"] == "AUTHENTICATION_ERROR"

    def test_login_missing_data(self, client):
        """Test login with missing required data."""
        response = client.post("/api/auth/login", json={})

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_login_invalid_json(self, client):
        """Test login with invalid JSON."""
        response = client.post("/api/auth/login", data="invalid json", content_type="application/json")

        assert response.status_code == 400

    def test_get_current_user_success(self, client, auth_headers, sample_user):
        """Test successful current user retrieval."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.get_current_user.return_value = {
                "user": sample_user.to_dict(),
                "message": "User information retrieved successfully",
            }

            response = client.get("/api/auth/me", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert "user" in data
            assert "message" in data

    def test_get_current_user_not_found(self, client, auth_headers):
        """Test current user retrieval when user not found."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.get_current_user.side_effect = ResourceNotFoundError("User", 1)

            response = client.get("/api/auth/me", headers=auth_headers)

            assert response.status_code == 404
            data = response.get_json()
            assert "error" in data

    def test_get_current_user_no_auth(self, client):
        """Test current user retrieval without authentication."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test current user retrieval with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_invalid_user_id(self, client, auth_headers):
        """Test current user retrieval with invalid user ID in token."""
        with patch("src.api.routes.auth_routes.get_jwt_identity", return_value="invalid_id"):
            response = client.get("/api/auth/me", headers=auth_headers)

            assert response.status_code == 401
            data = response.get_json()
            assert "error" in data

    def test_register_service_exception(self, client, sample_user_data):
        """Test user registration with service exception."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.register_user.side_effect = Exception("Database error")

            response = client.post("/api/auth/register", json=sample_user_data)

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_login_service_exception(self, client, sample_user_data):
        """Test user login with service exception."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.login_user.side_effect = Exception("Database error")

            login_data = {
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            }
            response = client.post("/api/auth/login", json=login_data)

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_get_current_user_service_exception(self, client, auth_headers):
        """Test current user retrieval with service exception."""
        with patch("src.api.routes.auth_routes.auth_service") as mock_service:
            mock_service.get_current_user.side_effect = Exception("Database error")

            response = client.get("/api/auth/me", headers=auth_headers)

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_register_validation_error_detailed(self, client):
        """Test user registration with detailed validation error."""
        invalid_data = {
            "email": "invalid-email",
            "password": "weak",
            "first_name": "",
            "last_name": "",
        }

        response = client.post("/api/auth/register", json=invalid_data)

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_login_validation_error(self, client):
        """Test login with validation error."""
        invalid_data = {"email": "invalid-email", "password": ""}

        response = client.post("/api/auth/login", json=invalid_data)

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_register_empty_request(self, client):
        """Test user registration with empty request body."""
        response = client.post("/api/auth/register")

        assert response.status_code == 400

    def test_login_empty_request(self, client):
        """Test user login with empty request body."""
        response = client.post("/api/auth/login")

        assert response.status_code == 400

    def test_get_current_user_missing_headers(self, client):
        """Test current user retrieval with missing headers."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_register_content_type_validation(self, client, sample_user_data):
        """Test user registration with wrong content type."""
        response = client.post(
            "/api/auth/register",
            data=json.dumps(sample_user_data),
            content_type="text/plain",
        )

        assert response.status_code == 400

    def test_login_content_type_validation(self, client, sample_user_data):
        """Test user login with wrong content type."""
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        response = client.post("/api/auth/login", data=json.dumps(login_data), content_type="text/plain")

        assert response.status_code == 400
