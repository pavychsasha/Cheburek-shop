from typing import Annotated
import contextlib

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
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
    q: Annotated[str | None, Query(max_length=150)] = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
    is_superuser: bool | None = None,
    page: Annotated[int, Query(ge=1, le=2000)] = 1,
    per_page: Annotated[int, Query(ge=1, le=200)] = 100,
):
    stmt = select(User)
    if q:
        stmt = stmt.where(User.email.ilike(f"%{q.strip()}%"))
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    if is_verified is not None:
        stmt = stmt.where(User.is_verified == is_verified)
    if is_superuser is not None:
        stmt = stmt.where(User.is_superuser == is_superuser)
    stmt = stmt.order_by(User.email).limit(per_page).offset((page - 1) * per_page)
    result = await session.execute(stmt)
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
