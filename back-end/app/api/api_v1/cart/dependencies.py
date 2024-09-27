from math import prod
from typing import Annotated
import uuid

from fastapi import Depends, Path, Request

from app.api.api_v1.cart.services import CartService


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
):
    # Use the CartService class method to retrieve the cart
    return await CartService.get_cart(session_id=session_id)
