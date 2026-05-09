from app.core.config import settings
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from .v1.products.controllers import router as products_router
from .v1.auth.controllers import router as auth_router
from .v1.users.controllers import router as users_router
from .v1.cart.controllers import router as cart_router
from .v1.orders.controllers import router as order_router
from .v1.admin.controllers import router as admin_router
from .v1.languages.controllers import router as languages_router
from .v1.settings.controllers import router as settings_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)
router.include_router(router=products_router, prefix=settings.api.v1.products)
router.include_router(router=auth_router, prefix=settings.api.v1.auth)
router.include_router(router=users_router, prefix=settings.api.v1.users)
router.include_router(router=cart_router, prefix=settings.api.v1.cart)
router.include_router(router=order_router, prefix=settings.api.v1.orders)
router.include_router(router=admin_router, prefix=settings.api.v1.admin)
router.include_router(router=languages_router, prefix=settings.api.v1.languages)
router.include_router(router=settings_router, prefix=settings.api.v1.settings)
