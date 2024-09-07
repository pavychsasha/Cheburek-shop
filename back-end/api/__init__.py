from core.config import settings
from fastapi import APIRouter

from .api_v1.products.controllers import router as products_router
from .api_v1.auth.controllers import router as auth_router

router = APIRouter()
router.include_router(router=products_router, prefix="/products")
router.include_router(router=auth_router, prefix=settings.api.v1.auth)
