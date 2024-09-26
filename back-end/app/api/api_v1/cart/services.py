from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request
import uuid


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
    async def update_cart(
        cls,
        session: AsyncIOMotorClient,
        updated_cart,
    ):
        await session["carts"].update_one(
            {"_id": updated_cart["_id"]},
            {
                "$set": {"items": updated_cart["items"]},
            },
        )

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

        await cls.update_cart(session=session, updated_cart=cart)
        return cart

    @classmethod
    async def delete_product_from_cart(
        cls,
        cart,
        session: AsyncIOMotorClient,
        product_id: uuid.UUID,
    ):
        await session["carts"].update_one(
            {"_id": cart["_id"]},
            {"$pull": {"items": {"product_id": product_id}}},
        )

    @classmethod
    async def delete_cart_items(
        cls,
        session: AsyncIOMotorClient,
        cart,
    ):
        await session["carts"].delete_many({"_id": cart["_id"]})

    @classmethod
    async def get_items_count(
        cls,
        session: AsyncIOMotorClient,
        cart,
    ):
        pipeline = [
            {"$match": {"_id": cart["_id"]}},  # Match the document by _id
            {"$unwind": "$items"},  # Unwind the items array
            {
                "$group": {"_id": None, "total_quantity": {"$sum": "$items.quantity"}}
            },  # Sum the quantity
        ]
        result = await session["carts"].aggregate(pipeline).to_list(length=None)
        return result[0]["total_quantity"] if result else 0
