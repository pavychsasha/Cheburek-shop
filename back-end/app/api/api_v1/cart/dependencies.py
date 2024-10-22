import uuid
from typing import Annotated, Optional

from app.api.api_v1.cart.services import CartService
from app.api.dependencies.authentication.fastapi_users import current_user_id
from app.api.dependencies.session import current_language, session_id
from app.core.models import sql_db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


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
