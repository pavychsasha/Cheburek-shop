import uuid

from app.api.api_v1.cart.services import CartService
from app.core.exceptions import ZeroProductsOrderError
from app.core.models import (Cart, CartItem, Order, OrderProductAssociation,
                             Product)
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class OrderService:
    @classmethod
    async def get_orders(cls, session: AsyncSession):
        stmt = (
            select(Order)
            .options(
                joinedload(Order.products)
                .selectinload(OrderProductAssociation.product)
                .selectinload(Product.translations)
            )
            .order_by(Order.created_at)
        )
        result = await session.execute(stmt)
        return result.unique().scalars().all()

    @classmethod
    async def add_products_to_order(
        cls,
        session: AsyncSession,
        order: Order,
        products: list[CartItem],
    ):
        """
        Add multiple products to an order.

        Args:
            session: The active database session.
            order: The order to which the products should be added.
            products_data: A list of dictionaries with 'product_id' and 'quantity'.

        Example of products_data:
        [
            {"product_id": <product_id_1>, "quantity": 2},
            {"product_id": <product_id_2>, "quantity": 1}
        ]
        """
        association_list = []
        for product in products:
            association_list.append(
                OrderProductAssociation(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=product.count,
                )
            )
        session.add_all(association_list)
        await session.commit()

    @classmethod
    async def make_order(cls, session: AsyncSession, mongo_cart: Cart):
        new_order = Order()
        if not mongo_cart.items:
            raise ZeroProductsOrderError()
        session.add(new_order)
        await session.commit()
        await cls.add_products_to_order(
            session=session,
            products=mongo_cart.items,
            order=new_order,
        )

        # cleaning up purchased cart
        await CartService.delete_cart_items(cart=mongo_cart)

    @classmethod
    async def delete_order(
        cls,
        session: AsyncSession,
        order_id: uuid.UUID,
    ):
        stmt = delete(Order).filter(Order.order_id == order_id)
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def delete_all_products(cls, session: AsyncSession):
        stmt = delete(Order)
        await session.execute(stmt)
        await session.commit()
