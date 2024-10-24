import pytest
from httpx import AsyncClient

from app.core.models import Product


class TestControllers:

    @pytest.mark.asyncio
    async def test_languages_defaulted_to_eng(self, client: AsyncClient):
        response = await client.get("/api/v1/languages/current_language")
        assert response.status_code == 200

        assert response.json() == {"language": "en"}

    @pytest.mark.asyncio
    async def test_change_language(self, client: AsyncClient, products: list[Product]):
        response = await client.post(
            "/api/v1/languages/change_language", params={"language": "ukr"}
        )
        assert response.status_code == 200

        invalid_language_change = await client.post(
            "/api/v1/languages/change_language",
            params={"language": "fr"},  # not presented in db
        )

        assert invalid_language_change.status_code == 404
        assert invalid_language_change.json() == {
            "detail": "language code fr' was not found"
        }
