from math import prod
from typing import Annotated, Optional
import uuid

from app.core.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, Path, Request

from app.api.api_v1.cart.services import CartService
from app.core.models import sql_db_helper
from app.api.dependencies.authentication.fastapi_users import (
    current_user_id,
)


async def session_id(request: Request) -> uuid.UUID:
    session_id: uuid.UUID | str | None = request.session.get("session_id")

    # If no session_id exists, create one
    if not session_id:
        session_id = uuid.uuid4()
        request.session["session_id"] = session_id

    if isinstance(session_id, str):
        session_id = uuid.UUID(session_id)
    return session_id


async def mongo_cart(
    session_id: Annotated[uuid.UUID, Depends(session_id)],
    user_id: Annotated[Optional[uuid.UUID], Depends(current_user_id)],
    sql_session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
):
    # Use the CartService class method to retrieve the cart
    return await CartService.get_cart(
        sql_session=sql_session, session_id=session_id, user_id=user_id
    )
