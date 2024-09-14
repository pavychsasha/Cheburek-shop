from typing import Annotated, Optional
import uuid

from app.core.models.user import User
from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.models import mongo_db_helper
from app.api.dependencies.authentication.fastapi_users import current_user
from app.api.api_v1.cart.services import CartService


async def mongo_cart(
    request: Request,
    session: Annotated[
        AsyncIOMotorClient, Depends(mongo_db_helper.mongo_session_dependency)
    ],
    current_user: Annotated[User, Depends(current_user)],
):
    # Use the CartService class method to retrieve the cart
    user_id: Optional[uuid.UUID] = current_user.id if current_user else None
    return await CartService.get_cart(session, request, user_id=user_id)
