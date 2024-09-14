from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request
import uuid
from datetime import datetime


class CartService:
    @classmethod
    async def get_cart(
        cls,
        session: AsyncIOMotorClient,
        request: Request,
        user_id: Optional[uuid.UUID] = None,
    ):
        session_id = request.session.get("session_id")

        # If no session_id exists, create one
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["session_id"] = session_id

        # Retrieve the cart based on the session_id
        session_cart = await session["carts"].find_one({"session_id": session_id})

        # If no cart exists, create a new empty cart for the session
        if not session_cart:
            new_cart = {"session_id": session_id, "items": []}
            await session["carts"].insert_one(new_cart)
            return new_cart

        return session_cart

    @classmethod
    async def add_item_to_cart(
        cls,
        session: AsyncIOMotorClient,
        cart,
        item,
    ):
        # Add or update the item in the cart
        for cart_item in cart["items"]:
            if cart_item["product_id"] == item.product_id:
                cart_item["quantity"] += item.quantity
                break
        else:
            cart["items"].append(item.dict())

        return cart
