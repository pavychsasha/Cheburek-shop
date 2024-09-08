from core.schemas.user import UserRead, UserUpdate
from fastapi import APIRouter
from api.dependencies.authentication.fastapi_users import fastapi_users
from api.dependencies.authentication import auth_backend

router = APIRouter(
    tags=["Users"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
