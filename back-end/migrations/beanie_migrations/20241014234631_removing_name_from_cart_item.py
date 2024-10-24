import uuid
from pydantic import Field
from beanie import Document, free_fall_migration
from app.core.models.db_helper import sql_db_helper
from app.api.v1.products.services import get_product


class OldCartItem(Document):
    product_id: uuid.UUID
    name: str
    price: float = Field(..., ge=0)
    count: int = Field(..., ge=0)
    image_src: str
    total_price: float = Field(..., ge=0)

    class Settings:
        name = "cart_items"


class NewCartItem(Document):
    product_id: uuid.UUID
    price: float = Field(..., ge=0)
    count: int = Field(..., ge=0)
    total_price: float = Field(..., ge=0)

    class Settings:
        name = "cart_items"


class Forward:

    @free_fall_migration(document_models=[OldCartItem, NewCartItem])
    async def remove_name_and_img(self, session):
        async with sql_db_helper.session_factory() as sql_session:
            async for old_cart_item in OldCartItem.find_all():
                product = await get_product(
                    session=sql_session, product_id=old_cart_item.product_id
                )
                total_price = old_cart_item.count * product.price
                new_note = NewCartItem(
                    id=old_cart_item.id,
                    product_id=old_cart_item.product_id,
                    price=product.price,
                    count=old_cart_item.count,
                    total_price=total_price,
                )
                await new_note.replace(session=session)


class Backward:
    @free_fall_migration(document_models=[OldCartItem, NewCartItem])
    async def title_to_name(self, session):
        async with sql_db_helper.session_factory() as sql_session:
            async for old_cart_item in NewCartItem.find_all():
                product = await get_product(
                    session=sql_session, product_id=old_cart_item.product_id
                )
                total_price = old_cart_item.count * product.price
                new_note = OldCartItem(
                    id=old_cart_item.id,
                    product_id=old_cart_item.product_id,
                    name=product.name,
                    price=product.price,
                    count=old_cart_item.count,
                    image_src=product.image_src,
                    total_price=total_price,
                )
                await new_note.replace(session=session)
