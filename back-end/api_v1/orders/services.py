from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload
from api_v1.orders.schemas import OrderCreate
from core.models import Order, OrderProductAssociation


from sqlalchemy.ext.asyncio import AsyncSession


import uuid


async def create_order(
    session: AsyncSession,
    products_data: dict,
    order_create_data: OrderCreate,
) -> Order:
    order = Order(
        **order_create_data.model_dump(),
    )
    session.add(order)
    await session.commit()
    return order


async def get_order(
    session: AsyncSession,
    order_id: uuid.UUID,
) -> Order:
    stmt = (
        select(Order)
        .where(Order.order_id == order_id)
        .options(
            joinedload(Order.products),
            joinedload(Order.rewards),
        )
    )
    order: Order | None = await session.scalar(stmt)
    return order


async def delete_order(
    session: AsyncSession,
    order_id: uuid.UUID,
) -> None:
    stmt = delete(Order).where(Order.order_id == order_id)
    await session.execute(stmt)
    await session.commit()


async def create_order_product(
    session: AsyncSession,
    create_order: OrderCreate,
) -> Order:
    # validation check, at least whether product id exists and so on
    order_product_list: list = []
    for product_id, prodict_quantity in create_order.products_data.items():
        order_product_list.append(
            OrderProductAssociation(
                order_id=create_order.order_id,
                product_id=product_id,
                quantity=prodict_quantity,
            )
        )
    session.add_all(order_product_list)
    await session.commit()
    order: Order = await get_order(session=session, order_id=create_order.order_id)
    return order
