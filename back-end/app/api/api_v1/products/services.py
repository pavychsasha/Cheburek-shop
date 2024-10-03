import uuid
from app.core.exceptions import (
    InvalidUuidError,
    ProductNameDuplicationError,
    ProductNotFoundError,
    InvalidSortFieldError,
    InvalidProductOrderError,
)
from sqlalchemy import delete, select, asc, desc, func
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import Product

from .schemas import (
    ProductCreate,
    ProductUpdate,
    ProductPartialUpdate,
    ProductBulkCreate,
)


def validate_uuid(uuid_str: str):
    """Utility function to validate UUID strings."""
    try:
        return uuid.UUID(uuid_str)
    except ValueError:
        raise InvalidUuidError(uuid_str=uuid_str)


async def get_products(
    session: AsyncSession, limit: int = 10, offset: int = 0
) -> list[Product]:
    """Fetch products with pagination."""
    stmt = (
        select(Product)
        .where(Product.deleted_at.is_(None))
        .order_by(Product.product_id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return result.scalars().all()  # type: ignore


async def get_product(
    session: AsyncSession,
    product_id: str | uuid.UUID,
) -> Product:
    """Fetch a single product by its ID with UUID validation."""
    # Validate UUID before querying
    if isinstance(product_id, str):
        product_id = validate_uuid(product_id)

    product = await session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise ProductNotFoundError(product_id)
    return product


from sqlalchemy.exc import ArgumentError


async def search_products(
    session: AsyncSession,
    category: str | None = None,
    sort_by: str | None = "price",
    order: str | None = "asc",
    name: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    """Search products with pagination, sorting, and filtering."""
    valid_sort_fields = ["name", "price", "category", "stock_quantity"]

    # Check if the sort_by field is valid
    if sort_by and sort_by not in valid_sort_fields:
        raise InvalidSortFieldError(f"'{sort_by}' is not a valid field for sorting.")

    # Construct the query
    query = select(Product).where(Product.deleted_at.is_(None))

    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))

    if category:
        query = query.where(Product.category == category)

    # Sort by field and order validation
    if order == "desc":
        try:
            query = query.order_by(desc(getattr(Product, sort_by)))
        except AttributeError:
            raise InvalidProductOrderError(f"'{order}' is not valid.")
    elif order == "asc":
        try:
            query = query.order_by(asc(getattr(Product, sort_by)))
        except AttributeError:
            raise InvalidProductOrderError(f"'{order}' is not valid.")
    elif order:
        raise InvalidProductOrderError(f"'{order}' is not a valid order.")

    # Add pagination
    query = query.limit(limit).offset(offset)

    result = await session.execute(query)
    return result.scalars().all()


async def create_product(session: AsyncSession, product_in: ProductCreate) -> Product:
    """Create a new product and ensure no duplicate names exist."""
    stmt = (
        select(Product)
        .where(Product.name == product_in.name)
        .options(load_only(Product.product_id))
    )
    result = await session.execute(stmt)
    if result.one_or_none():
        raise ProductNameDuplicationError(product_in.name)

    product = Product(**product_in.model_dump())
    session.add(product)
    await session.commit()
    return product


async def bulk_create_product(
    session: AsyncSession,
    products_in: ProductBulkCreate,
) -> ProductBulkCreate:
    """Bulk create products, ensuring no duplicates."""
    product_names = [product_in.name for product_in in products_in.products]

    # Check for duplicates in the incoming request before querying the database
    if len(product_names) != len(set(product_names)):
        raise ProductNameDuplicationError("Duplicate product names in request")

    stmt = select(Product).where(Product.name.in_(product_names))
    result = await session.execute(stmt)
    existing_products = result.scalars().all()

    if existing_products:
        existing_names = [product.name for product in existing_products]
        raise ProductNameDuplicationError(
            f"Products with names {existing_names} already exist."
        )

    products = [
        Product(**product_in.model_dump()) for product_in in products_in.products
    ]
    session.add_all(products)
    await session.commit()
    return products_in  # Return the created products as a list


async def update_product(
    session: AsyncSession,
    product_id: uuid.UUID,
    product_update: ProductUpdate | ProductPartialUpdate,
    partial: bool = False,
) -> Product:
    """Update an existing product, raising an error if it doesn't exist."""
    product = await get_product(session, product_id)
    # Ensure all DB calls are awaited properly
    for name, value in product_update.model_dump(exclude_unset=partial).items():
        setattr(product, name, value)
    await session.commit()
    return product


async def delete_product(
    session: AsyncSession,
    product_id: uuid.UUID,
) -> None:
    """Delete a product by its ID. Perform soft deletion by default."""
    await get_product(session, product_id)  # checking for product's existance
    await session.execute(delete(Product).where(Product.product_id == product_id))

    await session.commit()
