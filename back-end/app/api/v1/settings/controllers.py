from fastapi import APIRouter, status

from app.core.schemas.settings import PublicSettings
from app.core.services.store_settings import get_public_currency_settings

router = APIRouter(tags=["Settings"])


@router.get(
    "/public",
    response_model=PublicSettings,
    status_code=status.HTTP_200_OK,
)
async def get_public_settings():
    return PublicSettings(currency=await get_public_currency_settings())
