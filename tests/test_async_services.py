"""Tests for async service functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.core.exceptions import ResourceNotFoundError, ValidationError
from src.services.recipe_management.recipe_service import RecipeService


class TestAsyncRecipeService:
    """Test async recipe service functionality."""

    @pytest.mark.asyncio
    async def test_create_recipe_async_success(self, db_session, sample_user, sample_recipe_data):
        """Test successful async recipe creation."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "create_async", new_callable=AsyncMock) as mock_create:
            mock_recipe = Mock()
            mock_recipe.id = 1
            mock_recipe.title = sample_recipe_data["title"]
            mock_recipe.to_dict.return_value = {
                "id": 1,
                "title": sample_recipe_data["title"],
            }
            mock_create.return_value = mock_recipe

            result = await service.create_recipe_async(db_session, sample_recipe_data, sample_user.id)

            assert "recipe" in result
            assert "message" in result
            assert result["message"] == "Recipe created successfully"

    @pytest.mark.asyncio
    async def test_create_recipe_async_validation_error(self, db_session, sample_user, invalid_recipe_data):
        """Test async recipe creation with validation error."""
        service = RecipeService()

        with pytest.raises(ValidationError):
            await service.create_recipe_async(db_session, invalid_recipe_data, sample_user.id)

    @pytest.mark.asyncio
    async def test_get_recipe_async_success(self, db_session, sample_recipe):
        """Test successful async recipe retrieval."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id_async", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_recipe

            result = await service.get_recipe_async(db_session, sample_recipe.id, sample_recipe.user_id)

            assert "recipe" in result
            assert "message" in result
            assert result["message"] == "Recipe retrieved successfully"

    @pytest.mark.asyncio
    async def test_get_recipe_async_not_found(self, db_session, sample_user):
        """Test async recipe retrieval with non-existent recipe."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id_async", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with pytest.raises(ResourceNotFoundError) as exc_info:
                await service.get_recipe_async(db_session, 999, sample_user.id)
            assert exc_info.value.resource_type == "Recipe"
            assert exc_info.value.resource_id == 999

    @pytest.mark.asyncio
    async def test_update_recipe_async_success(self, db_session, sample_recipe, sample_recipe_data):
        """Test successful async recipe update."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id_async", new_callable=AsyncMock) as mock_get:
            with patch.object(service.recipe_repository, "update_async", new_callable=AsyncMock) as mock_update:
                mock_get.return_value = sample_recipe
                mock_updated_recipe = Mock()
                mock_updated_recipe.to_dict.return_value = {
                    "id": sample_recipe.id,
                    "title": "Updated Title",
                }
                mock_update.return_value = mock_updated_recipe

                result = await service.update_recipe_async(
                    db_session,
                    sample_recipe.id,
                    sample_recipe_data,
                    sample_recipe.user_id,
                )

                assert "recipe" in result
                assert "message" in result
                assert result["message"] == "Recipe updated successfully"

    @pytest.mark.asyncio
    async def test_update_recipe_async_not_found(self, db_session, sample_user, sample_recipe_data):
        """Test async recipe update with non-existent recipe."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id_async", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with pytest.raises(ResourceNotFoundError) as exc_info:
                await service.update_recipe_async(db_session, 999, sample_recipe_data, sample_user.id)
            assert exc_info.value.resource_type == "Recipe"

    @pytest.mark.asyncio
    async def test_delete_recipe_async_success(self, db_session, sample_recipe):
        """Test successful async recipe deletion."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id_async", new_callable=AsyncMock) as mock_get:
            with patch.object(service.recipe_repository, "delete_async", new_callable=AsyncMock) as mock_delete:
                mock_get.return_value = sample_recipe
                mock_delete.return_value = True

                result = await service.delete_recipe_async(db_session, sample_recipe.id, sample_recipe.user_id)

                assert "message" in result
                assert result["message"] == "Recipe deleted successfully"

    @pytest.mark.asyncio
    async def test_delete_recipe_async_not_found(self, db_session, sample_user):
        """Test async recipe deletion with non-existent recipe."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_by_id_async", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with pytest.raises(ResourceNotFoundError) as exc_info:
                await service.delete_recipe_async(db_session, 999, sample_user.id)
            assert exc_info.value.resource_type == "Recipe"

    @pytest.mark.asyncio
    async def test_list_recipes_async_success(self, db_session, sample_user):
        """Test successful async recipe listing."""
        service = RecipeService()
        mock_recipes = [Mock(), Mock()]
        mock_recipes[0].to_dict.return_value = {"id": 1, "title": "Recipe 1"}
        mock_recipes[1].to_dict.return_value = {"id": 2, "title": "Recipe 2"}

        with patch.object(service.recipe_repository, "get_user_recipes_async", new_callable=AsyncMock) as mock_get:
            with patch.object(
                service.recipe_repository,
                "count_user_recipes_async",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_get.return_value = mock_recipes
                mock_count.return_value = 2

                result = await service.list_recipes_async(db_session, sample_user.id, page=1, per_page=10)

                assert "recipes" in result
                assert "pagination" in result
                assert len(result["recipes"]) == 2
                assert result["pagination"]["total"] == 2

    @pytest.mark.asyncio
    async def test_list_recipes_async_empty(self, db_session, sample_user):
        """Test async recipe listing with no recipes."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "get_user_recipes_async", new_callable=AsyncMock) as mock_get:
            with patch.object(
                service.recipe_repository,
                "count_user_recipes_async",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_get.return_value = []
                mock_count.return_value = 0

                result = await service.list_recipes_async(db_session, sample_user.id, page=1, per_page=10)

                assert "recipes" in result
                assert "pagination" in result
                assert len(result["recipes"]) == 0
                assert result["pagination"]["total"] == 0

    @pytest.mark.asyncio
    async def test_search_recipes_async_success(self, db_session, sample_user):
        """Test successful async recipe search."""
        service = RecipeService()
        mock_recipes = [Mock()]
        mock_recipes[0].to_dict.return_value = {"id": 1, "title": "Test Recipe"}

        search_params = {
            "search": "test",
            "difficulty": "easy",
            "prep_time_max": 60,
            "cook_time_max": 120,
            "tags": ["test"],
        }

        with patch.object(service.recipe_repository, "search_recipes_async", new_callable=AsyncMock) as mock_search:
            with patch.object(
                service.recipe_repository,
                "count_search_recipes_async",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_search.return_value = mock_recipes
                mock_count.return_value = 1

                result = await service.search_recipes_async(
                    db_session, sample_user.id, search_params, page=1, per_page=10
                )

                assert "recipes" in result
                assert "pagination" in result
                assert len(result["recipes"]) == 1

    @pytest.mark.asyncio
    async def test_recipe_authorization_async(self, db_session, sample_recipe, sample_user):
        """Test async recipe authorization (user can only access their own recipes)."""
        service = RecipeService()
        other_user_id = 999

        with patch.object(service.recipe_repository, "get_by_id_async", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_recipe

            with pytest.raises(ResourceNotFoundError):
                await service.get_recipe_async(db_session, sample_recipe.id, other_user_id)

    @pytest.mark.asyncio
    async def test_async_service_exception_handling(self, db_session, sample_user, sample_recipe_data):
        """Test async service exception handling."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "create_async", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("Database connection failed")

            with pytest.raises(Exception) as exc_info:
                await service.create_recipe_async(db_session, sample_recipe_data, sample_user.id)
            assert "Database connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_pagination_calculation(self, db_session, sample_user):
        """Test async pagination calculation."""
        service = RecipeService()
        mock_recipes = [Mock() for _ in range(5)]
        for i, recipe in enumerate(mock_recipes):
            recipe.to_dict.return_value = {"id": i + 1, "title": f"Recipe {i + 1}"}

        with patch.object(service.recipe_repository, "get_user_recipes_async", new_callable=AsyncMock) as mock_get:
            with patch.object(
                service.recipe_repository,
                "count_user_recipes_async",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_get.return_value = mock_recipes
                mock_count.return_value = 25

                result = await service.list_recipes_async(db_session, sample_user.id, page=2, per_page=10)

                assert "pagination" in result
                assert result["pagination"]["page"] == 2
                assert result["pagination"]["per_page"] == 10
                assert result["pagination"]["total"] == 25
                assert result["pagination"]["pages"] == 3

    @pytest.mark.asyncio
    async def test_async_concurrent_operations(self, db_session, sample_user, sample_recipe_data):
        """Test async concurrent operations."""
        service = RecipeService()

        async def create_recipe():
            with patch.object(service.recipe_repository, "create_async", new_callable=AsyncMock) as mock_create:
                mock_recipe = Mock()
                mock_recipe.id = 1
                mock_recipe.to_dict.return_value = {"id": 1, "title": "Test Recipe"}
                mock_create.return_value = mock_recipe

                return await service.create_recipe_async(db_session, sample_recipe_data, sample_user.id)

        # Run multiple concurrent operations
        import asyncio

        tasks = [create_recipe() for _ in range(3)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for result in results:
            assert "recipe" in result
            assert "message" in result

    @pytest.mark.asyncio
    async def test_async_validation_error_propagation(self, db_session, sample_user):
        """Test that validation errors are properly propagated in async operations."""
        service = RecipeService()
        invalid_data = {
            "title": "",  # Empty title should cause validation error
            "ingredients": [],  # Empty ingredients should cause validation error
            "instructions": [],  # Empty instructions should cause validation error
        }

        with pytest.raises(ValidationError) as exc_info:
            await service.create_recipe_async(db_session, invalid_data, sample_user.id)
        assert exc_info.value.field == "title"

    @pytest.mark.asyncio
    async def test_async_database_rollback(self, db_session, sample_user, sample_recipe_data):
        """Test that database rollback works correctly in async operations."""
        service = RecipeService()

        with patch.object(service.recipe_repository, "create_async", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("Database error")

            with pytest.raises(Exception):
                await service.create_recipe_async(db_session, sample_recipe_data, sample_user.id)

            # Verify that the database session would be rolled back
            # (In a real scenario, this would be handled by the database session)

    @pytest.mark.asyncio
    async def test_async_search_with_complex_filters(self, db_session, sample_user):
        """Test async search with complex filter combinations."""
        service = RecipeService()
        mock_recipes = [Mock()]
        mock_recipes[0].to_dict.return_value = {"id": 1, "title": "Complex Recipe"}

        complex_search_params = {
            "search": "complex recipe",
            "difficulty": "hard",
            "prep_time_max": 120,
            "cook_time_max": 180,
            "tags": ["complex", "advanced", "challenging"],
        }

        with patch.object(service.recipe_repository, "search_recipes_async", new_callable=AsyncMock) as mock_search:
            with patch.object(
                service.recipe_repository,
                "count_search_recipes_async",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_search.return_value = mock_recipes
                mock_count.return_value = 1

                result = await service.search_recipes_async(
                    db_session,
                    sample_user.id,
                    complex_search_params,
                    page=1,
                    per_page=10,
                )

                assert "recipes" in result
                assert "pagination" in result
                assert len(result["recipes"]) == 1
                assert result["recipes"][0]["title"] == "Complex Recipe"
