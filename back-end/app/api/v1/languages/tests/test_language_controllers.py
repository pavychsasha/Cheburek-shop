import pytest


class TestLanguageController:

    @pytest.mark.asyncio
    async def test_get_all_languages(self, products, superuser_client):
        # Ensure that the test database has language entries, or mock the data.
        response = await superuser_client.get("/api/v1/languages/")
        assert response.status_code == 200
        languages = response.json()
        assert "en" in languages  # Adjust based on available languages in your setup
        assert "ukr" in languages
