from typing import Annotated, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends

from app.api.v1.cart.services import CartService
from app.core.models import sql_db_helper
from app.core.dependencies.session import session_id, current_language
from app.core.dependencies.authentication.fastapi_users_dependency import (
    current_user_id,
)


async def mongo_cart(
    session_id: Annotated[uuid.UUID, Depends(session_id)],
    user_id: Annotated[Optional[uuid.UUID], Depends(current_user_id)],
):
    # Use the CartService class method to retrieve the cart
    return await CartService.get_cart(
        session_id=session_id,
        user_id=user_id,
    )


async def mongo_cart_populated(
    session_id: Annotated[uuid.UUID, Depends(session_id)],
    user_id: Annotated[Optional[uuid.UUID], Depends(current_user_id)],
    sql_database: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    current_language: Annotated[str, Depends(current_language)],
):
    # Use the CartService class method to retrieve the cart
    return await CartService.get_session_cart_with_product_data(
        session_id=session_id,
        user_id=user_id,
        sql_session=sql_database,
        language=current_language,
    )
