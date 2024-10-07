from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import sql_db_helper
from app.core.models.cart import Cart

from app.api.api_v1.cart.schemas import CartItemModify, CartModel
from app.api.api_v1.cart.services import CartService
from app.api.api_v1.cart.dependencies import mongo_cart


router = APIRouter(
    tags=["Cart"],
)


# Get the cart
@router.get("/", status_code=status.HTTP_200_OK, response_model=CartModel)
async def get_cart(cart: Annotated[Cart, Depends(mongo_cart)]):
    """
    Retrieve the current cart for the user or session.

    This function retrieves the cart for the current user if logged in, or for the session
    if the user is not logged in. It merges the session cart with the user's cart if both
    exist. If no cart is found, a new cart is created.

    Returns:
        JSONResponse: The current cart with its items.
    """
    return cart


# Add item to cart
@router.patch("/add", status_code=status.HTTP_204_NO_CONTENT)
async def add_item_to_cart(
    item: CartItemModify,
    cart: Annotated[Cart, Depends(mongo_cart)],
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
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

    await CartService.add_item_to_cart(
        cart=cart,
        cart_item_model=item,
        sql_session=session,
    )


@router.patch("/subtract_product", status_code=status.HTTP_204_NO_CONTENT)
async def subtract_item_to_cart(
    product: CartItemModify,
    cart: Annotated[Cart, Depends(mongo_cart)],
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
    await CartService.subtract_product_from_cart(
        cart=cart,
        substract_product=product,
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_items(
    cart: Annotated[Cart, Depends(mongo_cart)],
):
    await CartService.delete_cart_items(cart)


@router.delete("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    product_id: uuid.UUID,
    cart: Annotated[Cart, Depends(mongo_cart)],
):
    await CartService.delete_product_from_cart(cart, product_id=product_id)
