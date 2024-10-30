import asyncio
import uuid
from sqlalchemy import event, update
from .models import Product, OrderProductAssociation


async def update_product_status(session_factory, product_id: uuid.UUID, status: str):
    """Update product status asynchronously."""
    async with session_factory() as session:
        await session.execute(
            update(OrderProductAssociation)
            .where(OrderProductAssociation.product_id == product_id)
            .values(product_status=status)
        )
        await session.commit()


def register_product_event_listeners(session_factory):
    @event.listens_for(Product, "before_update")
    def before_update_product(mapper, connection, target):
        # Schedule async task in the main event loop
        loop = asyncio.get_event_loop()
        loop.create_task(
            update_product_status(session_factory, target.product_id, "updated")
        )

    @event.listens_for(Product, "before_delete")
    def before_delete_product(mapper, connection, target):
        loop = asyncio.get_event_loop()
        loop.create_task(
            update_product_status(session_factory, target.product_id, "deleted")
        )
