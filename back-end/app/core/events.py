import asyncio
import uuid
from sqlalchemy import event, update
from sqlalchemy.orm.attributes import get_history
from app.core.models import Product, OrderProductAssociation, ProductTranslation


async def update_product_status(session_factory, product_id: uuid.UUID, status: str):
    """Update product status asynchronously."""
    async with session_factory() as session:
        await session.execute(
            update(OrderProductAssociation)
            .where(
                OrderProductAssociation.product_id == product_id,
            )
            .values(product_status=status)
        )
        await session.commit()


def register_product_event_listeners(session_factory):
    @event.listens_for(Product, "before_update")
    def before_update_product(mapper, connection, target):
        # Schedule async task in the main event loop
        fields_to_check = ["price", "category", "image_src"]  # Adjust as necessary
        is_real_update = any(
            get_history(target, field).has_changes() for field in fields_to_check
        )

        # If there was an actual change, update product status in OrderProductAssociation
        if is_real_update:
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

    @event.listens_for(ProductTranslation, "before_update")
    def before_update_product_translation(mapper, connection, target):
        # Check if fields in ProductTranslation were actually updated
        fields_to_check = ["product_name", "product_description"]  # Adjust as necessary
        is_real_update = any(
            get_history(target, field).has_changes() for field in fields_to_check
        )

        # If there was an actual change, update product status in OrderProductAssociation
        if is_real_update:
            loop = asyncio.get_event_loop()
            loop.create_task(
                update_product_status(session_factory, target.product_id, "updated")
            )
