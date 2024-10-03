from typing import Optional
import uuid


from beanie import DeleteRules, WriteRules
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProductNotFoundError

from app.api.api_v1.cart.schemas import CartItemModel, CartItemModify
from app.core.models import Cart, CartItem, Product
from app.api.api_v1.products.services import get_product


class CartService:

    @classmethod
    async def merge_carts(
        cls,
        sql_session: AsyncSession,
        session_cart: Cart,
        user_cart: Cart,
    ):

        for item in session_cart.items:
            item: CartItemModel
            await cls.add_item_to_cart(
                cart=user_cart,
                cart_item_model=item,
                sql_session=sql_session,
            )
        await user_cart.save()
        await session_cart.delete(link_rule=DeleteRules.DELETE_LINKS)
        return user_cart

    @classmethod
    async def get_session_cart(
        cls,
        session_id: Optional[uuid.UUID] = None,
    ) -> Optional[Cart]:
        if session_id:
            return await Cart.find_one(
                Cart.session_id == session_id,
                fetch_links=True,
            )

    @classmethod
    async def get_users_cart(
        cls,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Cart]:
        if user_id:
            return await Cart.find_one(
                Cart.user_id == user_id,
                fetch_links=True,
            )

    @classmethod
    async def get_cart(
        cls,
        sql_session: AsyncSession,
        session_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> Cart:

        session_cart: Optional[Cart] = await cls.get_session_cart(session_id=session_id)

        if not session_cart:
            # trying to find user cart first
            if user_id:
                user_cart = await cls.get_users_cart(user_id)
                if user_cart is not None:
                    return user_cart

            cart = Cart(session_id=session_id, items=[], total_count=0, total_price=0)
            await cart.save(link_rule=WriteRules.WRITE)
            return cart

        elif session_cart and not user_id:
            return session_cart
        else:
            user_cart = await cls.get_users_cart(user_id)
            if user_cart:
                return await cls.merge_carts(
                    session_cart=session_cart,
                    user_cart=user_cart,
                    sql_session=sql_session,
                )

            user_cart = Cart(
                user_id=user_id,
                items=session_cart.items,
                total_count=session_cart.total_count,
                total_price=session_cart.total_price,
            )
            await user_cart.save()
            await cls.delete_cart_items(cart=session_cart)
            return user_cart

    @classmethod
    async def find_product_in_cart(
        cls,
        cart: Cart,
        product_id: uuid.UUID,
    ) -> CartItem | None:
        for item in cart.items:
            item: CartItemModel
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

            cart.items.append(new_item)  # type: ignore

        # Update the cart's total count and total price
        cart.total_count = sum(item.count for item in cart.items)  # type: ignore
        cart.total_price = sum(item.total_price for item in cart.items)  # type: ignore

        await cart.save(link_rule=WriteRules.WRITE)

    @classmethod
    async def substitute_product_from_cart(
        cls,
        cart: Cart,
        substract_product: CartItemModify,
    ):
        product: CartItem | None = await cls.find_product_in_cart(
            cart,
            product_id=substract_product.product_id,
        )
        if product:
            if product.count <= substract_product.count:
                return await cls.delete_product_from_cart(
                    cart=cart,
                    product_id=substract_product.product_id,
                )

            sub_count = substract_product.count
            sub_total_price = sub_count * product.price

            product.count -= sub_count
            product.total_price -= sub_total_price
            cart.total_count -= sub_count
            cart.total_price -= sub_total_price

            await product.save()
            await cart.save()

    @classmethod
    async def delete_product_from_cart(
        cls,
        cart,
        product_id: uuid.UUID,
    ):
        product: Optional[CartItem] = await cls.find_product_in_cart(
            cart, product_id=product_id
        )
        if product:
            cart.total_count -= product.count
            cart.total_price -= product.total_price
            await product.delete()
            await cart.save()

    @classmethod
    async def delete_cart_items(
        cls,
        cart: CartItem,
    ):
        await cart.delete()
