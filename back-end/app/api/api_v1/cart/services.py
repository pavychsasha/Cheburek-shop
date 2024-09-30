from itertools import product
import uuid


from beanie import WriteRules
from beanie.operators import Set
from sqlalchemy.ext.asyncio import AsyncSession

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.exceptions import ProductNotFound

from app.api.api_v1.cart.schemas import CartItemModel
from app.core.models import Cart, CartItem, Product
from app.api.api_v1.products.services import get_product


class CartService:
    @classmethod
    async def get_cart(cls, session_id: uuid.UUID) -> Cart:

        cart = await Cart.find_one(
            Cart.session_id == session_id,
            fetch_links=True,
        )
        if cart is None:
            cart = Cart(session_id=session_id, items=[], total_count=0, total_price=0)
            await cart.save(link_rule=WriteRules.WRITE)

        return cart

    @classmethod
    async def find_product_in_cart(
        cls,
        cart: Cart,
        product_id: uuid.UUID,
    ) -> CartItem | None:
        for item in cart.items:
            if item.product_id == product_id:
                return item  # type: ignore

    @classmethod
    async def add_item_to_cart(
        cls,
        cart: Cart,
        cart_item_model: CartItemModel,
        sql_session: AsyncSession,
    ):
        cart_product_id: uuid.UUID = cart_item_model.product_id

        existing_product_in_cart = await cls.find_product_in_cart(cart, cart_product_id)
        if existing_product_in_cart:
            existing_product_in_cart.count += cart_item_model.count
            existing_product_in_cart.total_price += (
                cart_item_model.count * existing_product_in_cart.price
            )
        else:
            product_from_db: Product | None = await get_product(
                session=sql_session, product_id=cart_product_id
            )

            if not product_from_db:
                raise ProductNotFound(product_id=cart_product_id)

            new_item = CartItem(
                product_id=cart_product_id,
                count=cart_item_model.count,
                name=product_from_db.name,
                price=product_from_db.price,
                img_src=product_from_db.image_src,
                total_price=cart_item_model.count * product_from_db.price,
            )

            cart.items.append(new_item)
        # Update the cart's total count and total price
        cart.total_count = sum(item.count for item in cart.items)
        cart.total_price = sum(item.total_price for item in cart.items)

        await cart.save(link_rule=WriteRules.WRITE)

    @classmethod
    async def delete_product_from_cart(
        cls,
        cart,
        product_id: uuid.UUID,
    ):
        product: CartItem = await cls.find_product_in_cart(cart, product_id=product_id)
        cart.total_count -= product.count
        cart.total_price -= product.total_price
        await product.delete()
        await cart.save()

    @classmethod
    async def delete_cart_items(
        cls,
        cart,
    ):
        await cart.delete()
