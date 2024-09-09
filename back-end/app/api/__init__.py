from app.core.config import settings
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from .api_v1.products.controllers import router as products_router
from .api_v1.auth.controllers import router as auth_router
from .api_v1.users.controllers import router as users_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)
router.include_router(router=products_router, prefix=settings.api.v1.products)
router.include_router(router=auth_router, prefix=settings.api.v1.auth)
router.include_router(router=users_router, prefix=settings.api.v1.users)
