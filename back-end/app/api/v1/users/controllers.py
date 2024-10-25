from typing import Annotated

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import sql_db_helper
from app.core.schemas.user import UserRead, UserUpdate
from app.core.dependencies.authentication.fastapi_users_dependency import fastapi_users
from .services import UserService

router = APIRouter(
    tags=["Users"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)


@router.get("/", response_model=list[UserRead])
async def get_users(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
) -> list[UserRead]:
    return await UserService.get_users(session=session)
