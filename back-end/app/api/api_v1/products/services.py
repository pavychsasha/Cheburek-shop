import uuid
from typing import Optional

import math

from app.core.exceptions import (
    InvalidUuidError,
    ProductNameDuplicationError,
    ProductNotFoundError,
    InvalidSortFieldError,
    InvalidProductOrderError,
)
from sqlalchemy import delete, select, asc, desc, and_, update, func
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Product
from app.core.models.product_translations import ProductTranslation

from .schemas import (
    ProductCreate,
    ProductUpdate,
    ProductPartialUpdate,
    ProductBulkCreate,
    ProductResponse,
    Pagination,
    ProductPaginatedResponse,
)


def validate_uuid(uuid_str: str):
    """Utility function to validate UUID strings."""
    try:
        return uuid.UUID(uuid_str)
    except ValueError:
        raise InvalidUuidError(uuid_str=uuid_str)

async def get_products(
        session: AsyncSession,
        pagination_params: Pagination | None = None,
) -> list[Product]:
    """Fetch products with pagination."""
    stmt = select(Product).options(
        joinedload(Product.translations)
    ).order_by(Product.product_id)
    if pagination_params:
        stmt = stmt.limit(
            pagination_params.per_page
        ).offset((pagination_params.page - 1) * pagination_params.per_page)

    result = await session.execute(stmt)
    return result.unique().scalars().all()

async def localize_product(
        product: Product,
        language: str = "en"
) -> ProductResponse:
    for translation in product.translations:
        if translation.language_code == language:
            return ProductResponse(
                product_id=product.product_id,
                name=translation.product_name,
                description=translation.product_description,
                price=product.price,
                category=product.category,
                stock_quantity=product.stock_quantity,
                image_src=product.image_src,
            )

async def localize_products_list(
        products: list[Product], language : str = "en"
):
    localized_products: list[Optional[ProductResponse]] = []
    for product in products:
        localized_product = await localize_product(product, language)
        localized_products.append(localized_product)

    return localized_products

async def get_num_of_pages(session: AsyncSession, per_page: int,  stmt=None) -> int:
    if stmt is not None:
        count_products_stmt = select(func.count()).select_from(stmt)
    else:
        count_products_stmt = select(func.count()).select_from(Product)

    result = await session.execute(count_products_stmt)
    count_products = result.scalar()
    return math.ceil(count_products / per_page)

async def get_all_products_response(
    session: AsyncSession,
    pagination_params: Pagination = Pagination(per_page=10, page=1),
    current_language: str = "en",

) -> ProductPaginatedResponse:
    products = await get_products(
        session=session,
        pagination_params=pagination_params
    )
    num_of_pages = await get_num_of_pages(session=session, per_page=pagination_params.per_page)
    localized_products = await localize_products_list(products, current_language)


    return ProductPaginatedResponse(pages=num_of_pages, products=localized_products)


async def get_product(
    session: AsyncSession,
    product_id: str | uuid.UUID,
) -> Product:
    """Fetch a single product by its ID with UUID validation."""
    # Validate UUID before querying
    if isinstance(product_id, str):
        product_id = validate_uuid(product_id)

    stmt = select(Product).options(
        joinedload(Product.translations)
    ).where(
        Product.product_id == product_id,
    )

    result = await session.execute(stmt)
    product = result.unique().scalar()

    if not product:
        raise ProductNotFoundError(product_id)
    return product


async def search_products(
    session: AsyncSession,
    category: str | None = None,
    sort_by: str | None = None,
    order: str | None = None,
    name: str | None = None,
    pagination_params: Pagination | None = None,
    query_only = False
):
    """Search products with pagination, sorting, and filtering."""
    valid_sort_fields = ["name", "price", "category", "stock_quantity"]

    # Check if the sort_by field is valid
    if sort_by and sort_by not in valid_sort_fields:
        raise InvalidSortFieldError(f"'{sort_by}' is not a valid field for sorting.")

    # Construct the query
    stmt = select(Product).join(ProductTranslation).options(selectinload(Product.translations))

    if pagination_params is not None:
        stmt = stmt.limit(
            pagination_params.per_page
        ).offset((pagination_params.page - 1) * pagination_params.per_page)

    if name:
        name = name.strip()
        stmt = stmt.where(
            ProductTranslation.product_name.ilike(f"%{name}%"),
        )

    if category:
        stmt = stmt.where(Product.category == category)

    # Sort by field and order validation
    if sort_by:
        if sort_by == "name" or sort_by == "description":
            obj_to_sort = ProductTranslation
            sort_by = "product_name" if sort_by == "name" else "product_description"
        else:
            obj_to_sort = Product

        if order == "desc":
            try:
                stmt = stmt.order_by(desc(getattr(obj_to_sort, sort_by)))
            except AttributeError:
                raise InvalidProductOrderError(f"'{order}' is not valid.")
        elif order == "asc":
            try:
                stmt = stmt.order_by(asc(getattr(obj_to_sort, sort_by)))
            except AttributeError:
                raise InvalidProductOrderError(f"'{order}' is not valid.")
        elif order:
            raise InvalidProductOrderError(f"'{order}' is not a valid order.")

    if query_only:
        return stmt

    result = await session.execute(stmt)
    return result.scalars().all()

async def get_searched_products_response(
        session: AsyncSession,
        pagination_params: Pagination,
        category: str | None = None,
        sort_by: str | None = None,
        order: str | None = None,
        name: str | None = None,
        current_language: str = "en",
) -> ProductPaginatedResponse:

    products = await search_products(
        session=session,
        category=category,
        sort_by=sort_by,
        order=order,
        name=name,
        pagination_params=pagination_params,
    )
    products_query = await search_products(
        session=session,
        category=category,
        sort_by=sort_by,
        order=order,
        name=name,
        query_only=True
    )

    num_of_pages = await get_num_of_pages(session=session, per_page=pagination_params.per_page, stmt=products_query)

    localized_products = await localize_products_list(products=products, language=current_language)

    return ProductPaginatedResponse(pages=num_of_pages, products=localized_products)


async def create_product(session: AsyncSession, product_in: ProductCreate) -> Product:
    """Create a new product and ensure no duplicate names exist."""
    translation_names = []
    for translation in product_in.translations:
        translation_names.append(translation.product_name)

    # Check for duplicates in the incoming request before querying the database
    if len(translation_names) != len(set(translation_names)):
        raise ProductNameDuplicationError("Duplicate product names in request")

    stmt = select(ProductTranslation).where(ProductTranslation.product_name.in_(translation_names))
    result = await session.execute(stmt)
    if result.one_or_none():
        raise ProductNameDuplicationError(translation_names)

    translations = [
        ProductTranslation(**translation.model_dump())
        for translation
        in product_in.translations
    ]

    product = Product(
        price=product_in.price,
        category=product_in.category,
        stock_quantity=product_in.stock_quantity,
        image_src=product_in.image_src,
        translations=translations,
    )

    session.add(product)
    await session.commit()
    return product


async def bulk_create_product(
    session: AsyncSession,
    products_in: ProductBulkCreate,
) -> ProductBulkCreate:


    translation_names = []
    for product in products_in.products:
        for translation in product.translations:
            translation_names.append(translation.product_name)

    # Check for duplicates in the incoming request before querying the database
    if len(translation_names) != len(set(translation_names)):
        raise ProductNameDuplicationError("Duplicate product names in request")

    stmt = select(ProductTranslation).where(ProductTranslation.product_name.in_(translation_names))

    result = await session.execute(stmt)
    existing_products = result.scalars().all()

    if existing_products:
        existing_names = [translation.product_name for translation in existing_products]
        raise ProductNameDuplicationError(
            f"Products with names {existing_names} already exist."
        )

    products = []
    for product in products_in.products:
        translations = [
            ProductTranslation(**translation.model_dump())
            for translation
            in product.translations
        ]
        products.append(
            Product(
                price=product.price,
                category=product.category,
                stock_quantity=product.stock_quantity,
                image_src=product.image_src,
                translations=translations,
            )
        )

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
        if name == "translations":
            for translation in product_update.translations:
                stmt = update(ProductTranslation).where(
                    and_(
                        ProductTranslation.product_id == product_id,
                        ProductTranslation.language_code == translation.language_code,
                    )
                ).values(
                    **translation.model_dump(exclude_unset=partial)
                )
                await session.execute(stmt)
        else:
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


async def delete_products(
    session: AsyncSession,
    product_ids: list[uuid.UUID],
) -> None:
    """Delete a product by its ID. Perform soft deletion by default."""
    await session.execute(delete(Product).where(Product.product_id.in_(product_ids)))

    await session.commit()
