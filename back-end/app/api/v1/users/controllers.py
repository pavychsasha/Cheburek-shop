from typing import Annotated
import contextlib

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies.authentication.fastapi_users_dependency import (
    current_active_superuser,
    fastapi_users,
)
from app.core.dependencies.authentication.user_manager import get_user_manager
from app.core.dependencies.authentication.users import get_users_db
from app.core.models import User, sql_db_helper
from app.core.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(
    tags=["Users"],
)

get_users_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


@router.get(
    "/",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
)
async def list_users(
    session: Annotated[
        AsyncSession,
        Depends(sql_db_helper.session_dependency),
    ],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    result = await session.execute(select(User).order_by(User.email))
    return result.scalars().all()


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_create: UserCreate,
    session: Annotated[
        AsyncSession,
        Depends(sql_db_helper.session_dependency),
    ],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    async with get_users_db_context(session) as user_db:
        async with get_user_manager_context(user_db) as user_manager:
            try:
                return await user_manager.create(
                    user_create=user_create,
                    safe=False,
                )
            except UserAlreadyExists as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists.",
                ) from exc


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
