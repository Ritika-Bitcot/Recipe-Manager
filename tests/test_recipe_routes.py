"""Tests for recipe API routes."""

import json
from unittest.mock import patch

from src.core.exceptions import ResourceNotFoundError


class TestRecipeRoutes:
    """Test recipe route functionality."""

    def test_create_recipe_success(self, client, auth_headers, sample_recipe_data):
        """Test successful recipe creation."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.create_recipe.return_value = {
                "recipe": {"id": 1, "title": sample_recipe_data["title"]},
                "message": "Recipe created successfully",
            }

            response = client.post("/api/recipes", json=sample_recipe_data, headers=auth_headers)

            assert response.status_code == 201
            data = response.get_json()
            assert "recipe" in data
            assert "message" in data
            assert data["message"] == "Recipe created successfully"

    def test_create_recipe_no_auth(self, client, sample_recipe_data):
        """Test recipe creation without authentication."""
        response = client.post("/api/recipes", json=sample_recipe_data)

        assert response.status_code == 401

    def test_create_recipe_validation_error(self, client, auth_headers, invalid_recipe_data):
        """Test recipe creation with validation error."""
        response = client.post("/api/recipes", json=invalid_recipe_data, headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_create_recipe_missing_data(self, client, auth_headers):
        """Test recipe creation with missing required data."""
        response = client.post("/api/recipes", json={}, headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_create_recipe_invalid_json(self, client, auth_headers):
        """Test recipe creation with invalid JSON."""
        response = client.post(
            "/api/recipes",
            data="invalid json",
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_get_recipe_success(self, client, auth_headers, sample_recipe):
        """Test successful recipe retrieval."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.get_recipe.return_value = {
                "recipe": {"id": sample_recipe.id, "title": sample_recipe.title},
                "message": "Recipe retrieved successfully",
            }

            response = client.get(f"/api/recipes/{sample_recipe.id}", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert "recipe" in data
            assert "message" in data

    def test_get_recipe_not_found(self, client, auth_headers):
        """Test recipe retrieval with non-existent recipe."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.get_recipe.side_effect = ResourceNotFoundError("Recipe", 999)

            response = client.get("/api/recipes/999", headers=auth_headers)

            assert response.status_code == 404
            data = response.get_json()
            assert "error" in data
            assert data["error"] == "Not Found"

    def test_get_recipe_no_auth(self, client, sample_recipe):
        """Test recipe retrieval without authentication."""
        response = client.get(f"/api/recipes/{sample_recipe.id}")

        assert response.status_code == 401

    def test_get_recipe_invalid_id(self, client, auth_headers):
        """Test recipe retrieval with invalid ID."""
        response = client.get("/api/recipes/invalid", headers=auth_headers)

        assert response.status_code == 404

    def test_update_recipe_success(self, client, auth_headers, sample_recipe, sample_recipe_data):
        """Test successful recipe update."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.update_recipe.return_value = {
                "recipe": {"id": sample_recipe.id, "title": "Updated Title"},
                "message": "Recipe updated successfully",
            }

            response = client.put(
                f"/api/recipes/{sample_recipe.id}",
                json=sample_recipe_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.get_json()
            assert "recipe" in data
            assert "message" in data

    def test_update_recipe_not_found(self, client, auth_headers, sample_recipe_data):
        """Test recipe update with non-existent recipe."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.update_recipe.side_effect = ResourceNotFoundError("Recipe", 999)

            response = client.put("/api/recipes/999", json=sample_recipe_data, headers=auth_headers)

            assert response.status_code == 404
            data = response.get_json()
            assert "error" in data

    def test_update_recipe_no_auth(self, client, sample_recipe, sample_recipe_data):
        """Test recipe update without authentication."""
        response = client.put(f"/api/recipes/{sample_recipe.id}", json=sample_recipe_data)

        assert response.status_code == 401

    def test_update_recipe_validation_error(self, client, auth_headers, sample_recipe, invalid_recipe_data):
        """Test recipe update with validation error."""
        response = client.put(
            f"/api/recipes/{sample_recipe.id}",
            json=invalid_recipe_data,
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_delete_recipe_success(self, client, auth_headers, sample_recipe):
        """Test successful recipe deletion."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.delete_recipe.return_value = {"message": "Recipe deleted successfully"}

            response = client.delete(f"/api/recipes/{sample_recipe.id}", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert "message" in data
            assert data["message"] == "Recipe deleted successfully"

    def test_delete_recipe_not_found(self, client, auth_headers):
        """Test recipe deletion with non-existent recipe."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.delete_recipe.side_effect = ResourceNotFoundError("Recipe", 999)

            response = client.delete("/api/recipes/999", headers=auth_headers)

            assert response.status_code == 404
            data = response.get_json()
            assert "error" in data

    def test_delete_recipe_no_auth(self, client, sample_recipe):
        """Test recipe deletion without authentication."""
        response = client.delete(f"/api/recipes/{sample_recipe.id}")

        assert response.status_code == 401

    def test_delete_recipe_invalid_id(self, client, auth_headers):
        """Test recipe deletion with invalid ID."""
        response = client.delete("/api/recipes/invalid", headers=auth_headers)

        assert response.status_code == 404

    def test_list_recipes_success(self, client, auth_headers):
        """Test successful recipe listing."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.list_recipes.return_value = {
                "recipes": [{"id": 1, "title": "Recipe 1"}],
                "pagination": {"page": 1, "per_page": 10, "total": 1, "pages": 1},
            }

            response = client.get("/api/recipes", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert "recipes" in data
            assert "pagination" in data

    def test_list_recipes_with_pagination(self, client, auth_headers):
        """Test recipe listing with pagination parameters."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.list_recipes.return_value = {
                "recipes": [],
                "pagination": {"page": 2, "per_page": 5, "total": 0, "pages": 0},
            }

            response = client.get("/api/recipes?page=2&per_page=5", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert "pagination" in data

    def test_list_recipes_no_auth(self, client):
        """Test recipe listing without authentication."""
        response = client.get("/api/recipes")

        assert response.status_code == 401

    def test_list_recipes_invalid_pagination(self, client, auth_headers):
        """Test recipe listing with invalid pagination parameters."""
        response = client.get("/api/recipes?page=0&per_page=101", headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_search_recipes_success(self, client, auth_headers):
        """Test successful recipe search."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.search_recipes.return_value = {
                "recipes": [{"id": 1, "title": "Test Recipe"}],
                "pagination": {"page": 1, "per_page": 10, "total": 1, "pages": 1},
            }

            response = client.get("/api/recipes/search?q=test", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert "recipes" in data
            assert "pagination" in data

    def test_search_recipes_with_filters(self, client, auth_headers):
        """Test recipe search with filters."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.search_recipes.return_value = {
                "recipes": [],
                "pagination": {"page": 1, "per_page": 10, "total": 0, "pages": 0},
            }

            response = client.get(
                "/api/recipes/search?q=test&difficulty=easy&prep_time_max=60",
                headers=auth_headers,
            )

            assert response.status_code == 200

    def test_search_recipes_no_auth(self, client):
        """Test recipe search without authentication."""
        response = client.get("/api/recipes/search?q=test")

        assert response.status_code == 401

    def test_search_recipes_invalid_filters(self, client, auth_headers):
        """Test recipe search with invalid filters."""
        response = client.get(
            "/api/recipes/search?difficulty=invalid&prep_time_max=-1",
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_create_recipe_service_exception(self, client, auth_headers, sample_recipe_data):
        """Test recipe creation with service exception."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.create_recipe.side_effect = Exception("Database error")

            response = client.post("/api/recipes", json=sample_recipe_data, headers=auth_headers)

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_get_recipe_service_exception(self, client, auth_headers, sample_recipe):
        """Test recipe retrieval with service exception."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.get_recipe.side_effect = Exception("Database error")

            response = client.get(f"/api/recipes/{sample_recipe.id}", headers=auth_headers)

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_update_recipe_service_exception(self, client, auth_headers, sample_recipe, sample_recipe_data):
        """Test recipe update with service exception."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.update_recipe.side_effect = Exception("Database error")

            response = client.put(
                f"/api/recipes/{sample_recipe.id}",
                json=sample_recipe_data,
                headers=auth_headers,
            )

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_delete_recipe_service_exception(self, client, auth_headers, sample_recipe):
        """Test recipe deletion with service exception."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.delete_recipe.side_effect = Exception("Database error")

            response = client.delete(f"/api/recipes/{sample_recipe.id}", headers=auth_headers)

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_list_recipes_service_exception(self, client, auth_headers):
        """Test recipe listing with service exception."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.list_recipes.side_effect = Exception("Database error")

            response = client.get("/api/recipes", headers=auth_headers)

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_search_recipes_service_exception(self, client, auth_headers):
        """Test recipe search with service exception."""
        with patch("src.api.routes.recipe_routes.recipe_service") as mock_service:
            mock_service.search_recipes.side_effect = Exception("Database error")

            response = client.get("/api/recipes/search?q=test", headers=auth_headers)

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_create_recipe_empty_request(self, client, auth_headers):
        """Test recipe creation with empty request body."""
        response = client.post("/api/recipes", headers=auth_headers)

        assert response.status_code == 400

    def test_update_recipe_empty_request(self, client, auth_headers, sample_recipe):
        """Test recipe update with empty request body."""
        response = client.put(f"/api/recipes/{sample_recipe.id}", headers=auth_headers)

        assert response.status_code == 400

    def test_create_recipe_content_type_validation(self, client, auth_headers, sample_recipe_data):
        """Test recipe creation with wrong content type."""
        response = client.post(
            "/api/recipes",
            data=json.dumps(sample_recipe_data),
            content_type="text/plain",
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_update_recipe_content_type_validation(self, client, auth_headers, sample_recipe, sample_recipe_data):
        """Test recipe update with wrong content type."""
        response = client.put(
            f"/api/recipes/{sample_recipe.id}",
            data=json.dumps(sample_recipe_data),
            content_type="text/plain",
            headers=auth_headers,
        )

        assert response.status_code == 400
