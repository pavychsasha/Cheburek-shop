from telnetlib import STATUS
from fastapi import APIRouter, Depends, status
from typing import Annotated

from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.models import mongo_db_helper
from app.api.api_v1.cart.schemas import CartItem, CartUpdate, Cart
from app.api.api_v1.cart.services import CartService
from app.api.api_v1.cart.dependencies import mongo_cart


# Custom encoder to handle ObjectId
def custom_jsonable_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)  # Convert ObjectId to a string
    return jsonable_encoder(obj, custom_encoder={ObjectId: str})


router = APIRouter(
    tags=["Cart"],
)


# Get the cart
@router.get("/")
async def get_cart(cart=Depends(mongo_cart)):
    """
    Retrieve the current cart for the user or session.

    This function retrieves the cart for the current user if logged in, or for the session
    if the user is not logged in. It merges the session cart with the user's cart if both
    exist. If no cart is found, a new cart is created.

    Returns:
        JSONResponse: The current cart with its items.
    """
    return JSONResponse(content=custom_jsonable_encoder(cart))


# Add item to cart
@router.post("/add")
async def add_item_to_cart(
    item: CartItem,
    session: Annotated[
        AsyncIOMotorClient, Depends(mongo_db_helper.mongo_session_dependency)
    ],
    cart=Depends(mongo_cart),
):
    """
    Add an item to the current cart.

    This function allows adding an item to the cart for the current session or user.
    If the item already exists in the cart, its quantity will be updated. If not, the
    item will be added to the list of items in the cart.

    Args:
        item (CartItem): The item to be added to the cart.
        cart: The current cart of the session/user.
        session: The MongoDB session for accessing the database.

    Returns:
        JSONResponse: A message confirming the addition of the item to the cart.
    """
    # Use the CartService class method to add the item to the cart
    updated_cart = await CartService.add_item_to_cart(session, cart, item)

    # Save the updated cart in MongoDB
    await session["carts"].update_one(
        {"_id": cart["_id"]}, {"$set": {"items": updated_cart["items"]}}
    )

    return {"message": "Item added to cart"}


# Get the cart item count
@router.get("/item-count", status_code=status.HTTP_200_OK)
async def get_cart_item_count(cart=Depends(mongo_cart)):
    """
    Retrieve the total number of items in the current cart.

    This function calculates the total quantity of items in the current user's or session's
    cart and returns the count.

    Returns:
        JSONResponse: The total number of items in the cart.
    """
    total_items = sum(item["quantity"] for item in cart["items"])
    return {"total_items": total_items}


# Update the cart
@router.patch("/update", status_code=status.HTTP_201_CREATED)
async def update_cart(
    cart_update: CartUpdate,
    session=Depends(mongo_db_helper.mongo_session_dependency),
    cart=Depends(mongo_cart),
):
    """
    Update the items in the cart.

    This function updates the current cart with a new set of items, replacing the previous items.
    The new cart items are passed through the `CartUpdate` model.

    Args:
        cart_update (CartUpdate): The updated items to be saved in the cart.
        cart: The current cart of the session/user.
        session: The MongoDB session for accessing the database.

    Returns:
        JSONResponse: The updated cart after the changes.
    """
    cart_update_dict = cart_update.model_dump()

    # Save the updated cart to MongoDB
    await session["carts"].update_one(
        {"_id": cart["_id"]},
        {
            "$set": {"items": cart_update_dict["items"]},
        },
    )
    return JSONResponse(content=custom_jsonable_encoder(cart))
