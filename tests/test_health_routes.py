"""Tests for health check routes."""

from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from src.api.routes.health_routes import health_bp


class TestHealthRoutes:
    """Test health check route functionality."""

    def test_health_check_success(self, app):
        """Test basic health check endpoint."""
        with app.test_client() as client:
            # Execute
            response = client.get("/api/health")

            # Assert
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "ok"
            assert data["message"] == "Recipe Manager API is running"

    def test_readiness_check_success(self, app):
        """Test readiness check with successful database connection."""
        with app.test_client() as client:
            # Execute
            response = client.get("/api/health/ready")

            # Assert
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "ready"
            assert data["message"] == "Recipe Manager API is ready"
            assert data["database"] == "connected"

    def test_readiness_check_database_error(self, app):
        """Test readiness check with database connection error."""
        with app.test_client() as client:
            with patch("src.api.routes.health_routes.db.session.execute") as mock_execute:
                # Setup
                mock_execute.side_effect = SQLAlchemyError("Database connection failed")

                # Execute
                response = client.get("/api/health/ready")

                # Assert
                assert response.status_code == 503
                data = response.get_json()
                assert data["status"] == "not ready"
                assert data["message"] == "Recipe Manager API is not ready"
                assert data["database"] == "disconnected"
                assert "Database connection failed" in data["error"]

    def test_readiness_check_general_exception(self, app):
        """Test readiness check with general exception."""
        with app.test_client() as client:
            with patch("src.api.routes.health_routes.db.session.execute") as mock_execute:
                # Setup
                mock_execute.side_effect = Exception("Unexpected error")

                # Execute
                response = client.get("/api/health/ready")

                # Assert
                assert response.status_code == 503
                data = response.get_json()
                assert data["status"] == "not ready"
                assert data["message"] == "Recipe Manager API is not ready"
                assert data["database"] == "disconnected"
                assert data["error"] == "Unexpected error"

    def test_readiness_check_connection_timeout(self, app):
        """Test readiness check with connection timeout."""
        with app.test_client() as client:
            with patch("src.api.routes.health_routes.db.session.execute") as mock_execute:
                # Setup
                mock_execute.side_effect = SQLAlchemyError("Connection timeout")

                # Execute
                response = client.get("/api/health/ready")

                # Assert
                assert response.status_code == 503
                data = response.get_json()
                assert data["status"] == "not ready"
                assert "Connection timeout" in data["error"]

    def test_health_check_methods(self, app):
        """Test that health endpoints only accept GET requests."""
        with app.test_client() as client:
            # Test POST to health check
            response = client.post("/api/health")
            assert response.status_code == 405  # Method Not Allowed

            # Test POST to readiness check
            response = client.post("/api/health/ready")
            assert response.status_code == 405  # Method Not Allowed

    def test_health_check_blueprint_registration(self, app):
        """Test that health blueprint is properly registered."""
        # Check if blueprint is registered
        assert health_bp.name == "health"
        assert health_bp.url_prefix == "/api/health"

        # Check if routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert "/api/health" in rules
        assert "/api/health/ready" in rules

    def test_health_check_response_format(self, app):
        """Test that health check responses have correct format."""
        with app.test_client() as client:
            # Test basic health check format
            response = client.get("/api/health")
            data = response.get_json()

            assert "status" in data
            assert "message" in data
            assert isinstance(data["status"], str)
            assert isinstance(data["message"], str)

    def test_readiness_check_response_format_success(self, app):
        """Test that readiness check success response has correct format."""
        with app.test_client() as client:
            response = client.get("/api/health/ready")
            data = response.get_json()

            assert "status" in data
            assert "message" in data
            assert "database" in data
            assert isinstance(data["status"], str)
            assert isinstance(data["message"], str)
            assert isinstance(data["database"], str)

    def test_readiness_check_response_format_error(self, app):
        """Test that readiness check error response has correct format."""
        with app.test_client() as client:
            with patch("src.api.routes.health_routes.db.session.execute") as mock_execute:
                mock_execute.side_effect = Exception("Test error")

                response = client.get("/api/health/ready")
                data = response.get_json()

                assert "status" in data
                assert "message" in data
                assert "database" in data
                assert "error" in data
                assert isinstance(data["status"], str)
                assert isinstance(data["message"], str)
                assert isinstance(data["database"], str)
                assert isinstance(data["error"], str)
