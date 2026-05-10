from fastapi import APIRouter, status

from app.core.schemas.settings import PublicSettings
from app.core.services.store_settings import (
    get_category_media_settings,
    get_product_language_settings,
    get_public_currency_settings,
)

router = APIRouter(tags=["Settings"])


@router.get(
    "/public",
    response_model=PublicSettings,
    status_code=status.HTTP_200_OK,
)
async def get_public_settings():
    return PublicSettings(
        currency=await get_public_currency_settings(),
        product_languages=await get_product_language_settings(),
        category_media=get_category_media_settings(),
    )
