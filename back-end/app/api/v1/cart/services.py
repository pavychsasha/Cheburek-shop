import logging
from typing import Optional
import uuid


from beanie import DeleteRules, WriteRules
from beanie.operators import In
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas.products import (
    ProductResponse,
    ProductUpdate,
    ProductPartialUpdate,
)
from app.core.exceptions import ProductCartNotFoundError, ProductNotFoundError

from app.core.schemas.cart import (
    CartItemModel,
    CartItemModify,
    CartItemResponse,
    CartModelResponse,
)
from app.core.models import Cart, CartItem, Product
from app.api.v1.products.services import ProductsService


class CartService:

    @classmethod
    async def merge_carts(cls, session_cart: Cart, user_cart: Cart):
        """Merge items from session cart into user cart."""
        logging.info(
            f"Merging carts: session_cart={session_cart.id}, user_cart={user_cart.id}"
        )

        items_map = {item.product_id: item for item in user_cart.items}

        for session_item in session_cart.items:
            if session_item.product_id in items_map:
                existing_item = items_map[session_item.product_id]
                existing_item.count += session_item.count
                existing_item.total_price += session_item.total_price
            else:
                user_cart.items.append(session_item)

        user_cart.total_count = sum(item.count for item in user_cart.items)
        user_cart.total_price = sum(item.total_price for item in user_cart.items)

        await user_cart.save()
        await session_cart.delete(link_rule=DeleteRules.DELETE_LINKS)
        logging.info(f"Cart merged successfully.")
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
    async def get_session_cart_with_product_data(
        cls,
        sql_session: AsyncSession,
        session_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        language: str = "en",
    ):
        cart = await cls.get_cart(
            session_id=session_id,
            user_id=user_id,
        )
        product_cart_items = []
        if cart and cart.items:
            for cart_item in cart.items:
                cart_item: CartItem
                product = await ProductsService.get_product(
                    session=sql_session,
                    product_id=cart_item.product_id,
                )
                localized_product: ProductResponse = (
                    await ProductsService.localize_product(
                        product=product,
                        language=language,
                    )
                )
                product_cart_items.append(
                    CartItemResponse(
                        product_id=cart_item.product_id,
                        name=localized_product.name,
                        image_src=localized_product.image_src,
                        price=cart_item.price,
                        count=cart_item.count,
                        total_price=cart_item.total_price,
                    )
                )
            return CartModelResponse(
                items=product_cart_items,
                total_count=cart.total_count,
                total_price=cart.total_price,
            )
        return CartModelResponse(
            items=[],
            total_count=0,
            total_price=0,
        )

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
            product_from_db: Product | None = await ProductsService.get_product(
                session=sql_session, product_id=cart_product_id
            )

            if not product_from_db:
                raise ProductNotFoundError(product_id=cart_product_id)

            new_item = CartItem(
                product_id=cart_product_id,
                count=cart_item_model.count,
                price=product_from_db.price,
                total_price=cart_item_model.count * product_from_db.price,
            )

            cart.items.append(new_item)  # type: ignore

        # Update the cart's total count and total price
        cart.total_count = sum(item.count for item in cart.items)  # type: ignore
        cart.total_price = sum(item.total_price for item in cart.items)  # type: ignore

        await cart.save(link_rule=WriteRules.WRITE)

    @classmethod
    async def subtract_product_from_cart(
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
            return

        raise ProductCartNotFoundError(product_id=product_id)

    @classmethod
    async def delete_cart_items(
        cls,
        cart: CartItem,
    ):
        await cart.delete()

    @classmethod
    async def remove_cart_item_references(cls, product_ids: list[uuid.UUID]):
        cart_items_to_delete: list[CartItem] = await CartItem.find(
            In(CartItem.product_id, product_ids)
        ).to_list()

        cart_item_ids = [item.id for item in cart_items_to_delete]
        await CartItem.find(In(CartItem.product_id, product_ids)).delete(
            link_rule=DeleteRules.DELETE_LINKS
        )

        if cart_item_ids:
            carts_with_items = await Cart.find(In(Cart.items, cart_item_ids)).to_list()

            for cart in carts_with_items:
                for product_id in product_ids:
                    await cls.delete_product_from_cart(cart=cart, product_id=product_id)

    @classmethod
    async def update_cart_products_info(
        cls, products: list[ProductUpdate | ProductPartialUpdate]
    ):
        """
        Update CartItems and recalculate total_price for all Carts that contain the updated items.

        Args:
            products (list[ProductUpdate | ProductPartialUpdate]): List of product updates with product_id and new price.
        """
        affected_cart_ids = set()

        # Step 1: Update CartItems with matching product_id
        for product in products:
            if product.price:
                # Find CartItems with the matching product_id
                cart_items_to_update = await CartItem.find(
                    CartItem.product_id == product.product_id
                ).to_list()

                # Update each CartItem's price and total_price
                for cart_item in cart_items_to_update:
                    cart_item.price = product.price
                    cart_item.total_price = cart_item.count * product.price
                    await cart_item.save(link_rule=WriteRules.WRITE)

                    # Step 2: Find all Carts containing this updated CartItem
                    carts = await Cart.find(
                        In(
                            [item.product_id for item in Cart.items],
                            [product.product_id],
                        )
                    ).to_list()

                    # Collect affected cart IDs
                    for cart in carts:
                        affected_cart_ids.add(cart.id)

        # Step 3: Recalculate total_price for each affected Cart
        for cart_id in affected_cart_ids:
            cart = await Cart.get(cart_id)
            if cart:
                # Recalculate total_price by summing up the total_price of all items in the cart
                cart_items = await CartItem.find(
                    In(CartItem.id, [item.id for item in cart.items])
                ).to_list()
                cart.total_price = sum(item.total_price for item in cart_items)
                await cart.save(link_rule=WriteRules.WRITE)
