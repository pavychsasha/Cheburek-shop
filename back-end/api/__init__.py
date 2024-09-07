from fastapi import APIRouter

from .api_v1.products.controllers import router as products_router

router = APIRouter()
router.include_router(router=products_router, prefix="/products")
