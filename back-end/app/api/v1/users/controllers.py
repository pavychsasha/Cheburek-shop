from app.core.schemas.user import UserRead, UserUpdate
from fastapi import APIRouter
from app.core.dependencies.authentication.fastapi_users_dependency import fastapi_users

router = APIRouter(
    tags=["Users"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
