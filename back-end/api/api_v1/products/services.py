import uuid
from sqlalchemy import delete, select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product

from .schemas import ProductCreate, ProductUpdate, ProductPartialUpdate


async def get_products(session: AsyncSession) -> list[Product]:
    stmt = select(Product).order_by(Product.product_id)
    result: Result = await session.execute(stmt)
    products = result.scalars()
    return list(products)


async def get_product(
    session: AsyncSession,
    product_id: uuid.UUID,
) -> Product | None:
    return await session.get(Product, product_id)


async def create_product(session: AsyncSession, product_in: ProductCreate) -> Product:
    product = Product(**product_in.model_dump())
    session.add(product)
    await session.commit()
    return product


async def update_product(
    session: AsyncSession,
    product: Product,
    product_update: ProductUpdate | ProductPartialUpdate,
    partial: bool = False,
) -> Product:
    for name, value in product_update.model_dump(exclude_unset=partial).items():
        setattr(product, name, value)
    await session.commit()
    return product


async def delete_product(
    session: AsyncSession,
    product_id: uuid.UUID,
) -> None:
    stmt = delete(Product).where(Product.product_id == product_id)
    await session.execute(stmt)
    await session.commit()
