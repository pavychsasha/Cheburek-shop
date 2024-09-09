import uuid
from app.core.exceptions import ProductNameDuplicationError
from sqlalchemy import delete, select, asc, desc
from sqlalchemy.orm import load_only

from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import Product

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


async def search_products(
    session: AsyncSession,
    category: str | None = None,
    sort_by: str | None = "price",
    order: str | None = "asc",
    name: str | None = None,
    query_only: bool = False,
):

    query = select(Product)

    if category:
        query = query.where(Product.category.ilike(f"%{name}%"))

    if sort_by in ["name", "price"]:
        if order == "desc":
            query = query.order_by(desc(getattr(Product, sort_by)))

    if not query_only:
        result = await session.execute(query)
        return result.scalars().all()
    return query


async def create_product(session: AsyncSession, product_in: ProductCreate) -> Product:
    product = Product(**product_in.model_dump())
    stmt = (
        select(Product)
        .where(Product.name == product_in.name)
        .options(load_only(Product.product_id))
    )
    result = await session.execute(stmt)
    if result.one_or_none():
        raise ProductNameDuplicationError(product_in.name)
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
