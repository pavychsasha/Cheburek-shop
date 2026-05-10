import logging
import uuid
from typing import Optional

import math

from app.core.caching.decorators import memoize
from app.core.exceptions import (
    InvalidUuidError,
    ProductNameDuplicationError,
    ProductNotFoundError,
    InvalidSortFieldError,
    InvalidProductOrderError,
)
from sqlalchemy import delete, select, asc, desc, and_, update, func
from sqlalchemy.orm import joinedload, selectinload, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import redis_db_helper
from app.core.models import Product
from app.core.models.product_tag import ProductTag
from app.core.models.product_translations import ProductTranslation

from app.core.schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductPartialUpdate,
    ProductBulkCreate,
    ProductResponse,
    Pagination,
    ProductPaginatedResponse,
)
from app.core.services.product_translations import complete_product_translations


logger = logging.getLogger(__name__)


def validate_uuid(uuid_str: str):
    """Utility function to validate UUID strings."""
    try:
        return uuid.UUID(uuid_str)
    except ValueError:
        raise InvalidUuidError(uuid_str=uuid_str)


class ProductsService:
    @staticmethod
    def _normalize_tag_names(tag_names: list[str] | None) -> list[str]:
        if not tag_names:
            return []
        normalized = [
            tag.strip().lower()
            for tag in tag_names
            if tag and tag.strip()
        ]
        return list(dict.fromkeys(normalized))

    @classmethod
    async def _resolve_tags(
        cls,
        session: AsyncSession,
        tag_names: list[str] | None,
    ) -> list[ProductTag]:
        normalized_names = cls._normalize_tag_names(tag_names)
        if not normalized_names:
            return []

        existing_result = await session.execute(
            select(ProductTag).where(ProductTag.name.in_(normalized_names))
        )
        existing_tags = {tag.name: tag for tag in existing_result.scalars().all()}
        created = False
        resolved_tags = []
        for tag_name in normalized_names:
            tag = existing_tags.get(tag_name)
            if tag is None:
                tag = ProductTag(name=tag_name)
                session.add(tag)
                existing_tags[tag_name] = tag
                created = True
            resolved_tags.append(tag)
        if created:
            await session.flush()
        return resolved_tags

    @classmethod
    async def _sync_product_tags(
        cls,
        session: AsyncSession,
        product: Product,
        tag_names: list[str] | None,
    ) -> None:
        product.tag_links = await cls._resolve_tags(session, tag_names)

    @classmethod
    async def get_products(
        cls,
        session: AsyncSession,
        pagination_params: Pagination | None = None,
    ) -> list[Product]:
        """Fetch products with pagination."""
        stmt = (
            select(Product)
            .options(
                joinedload(Product.translations),
                selectinload(Product.tag_links),
            )
            .order_by(Product.product_id)
        )
        if pagination_params:
            stmt = stmt.limit(pagination_params.per_page).offset(
                (pagination_params.page - 1) * pagination_params.per_page
            )

        result = await session.execute(stmt)
        return result.unique().scalars().all()

    @classmethod
    async def localize_product(
        cls, product: Product, language: str = "en"
    ) -> ProductResponse:
        fallback_translation = None
        for translation in product.translations:
            if translation.language_code == "en":
                fallback_translation = translation
            if translation.language_code == language:
                return ProductResponse(
                    product_id=product.product_id,
                    name=translation.product_name,
                    description=translation.product_description,
                    price=product.price,
                    category=product.category,
                    stock_quantity=product.stock_quantity,
                    image_src=product.image_src,
                    tags=product.tags,
                )
        if fallback_translation is None and product.translations:
            fallback_translation = product.translations[0]
        if fallback_translation is None:
            raise ProductNotFoundError(product.product_id)

        return ProductResponse(
            product_id=product.product_id,
            name=fallback_translation.product_name,
            description=fallback_translation.product_description,
            price=product.price,
            category=product.category,
            stock_quantity=product.stock_quantity,
            image_src=product.image_src,
            tags=product.tags,
        )

    @classmethod
    async def localize_products_list(
        cls, products: list[Product], language: str = "en"
    ):
        localized_products: list[Optional[ProductResponse]] = []
        for product in products:
            localized_product = await cls.localize_product(product, language)
            localized_products.append(localized_product)

        return localized_products

    @classmethod
    async def get_num_of_pages(
        cls, session: AsyncSession, per_page: int, stmt=None
    ) -> int:
        if stmt is not None:
            count_products_stmt = select(func.count()).select_from(
                stmt.order_by(None).subquery()
            )
        else:
            count_products_stmt = select(func.count()).select_from(Product)

        result = await session.execute(count_products_stmt)
        count_products = result.scalar()
        return math.ceil(count_products / per_page)

    @classmethod
    @memoize()
    async def get_all_products_response(
        cls,
        session: AsyncSession,
        pagination_params: Pagination = Pagination(per_page=10, page=1),
        current_language: str = "en",
    ) -> ProductPaginatedResponse:
        products = await cls.get_products(
            session=session, pagination_params=pagination_params
        )
        num_of_pages = await cls.get_num_of_pages(
            session=session, per_page=pagination_params.per_page
        )
        localized_products = await cls.localize_products_list(
            products, current_language
        )

        return ProductPaginatedResponse(pages=num_of_pages, products=localized_products)

    @classmethod
    async def get_product(
        cls,
        session: AsyncSession,
        product_id: str | uuid.UUID,
    ) -> Product:
        """Fetch a single product by its ID with UUID validation."""
        # Validate UUID before querying
        if isinstance(product_id, str):
            product_id = validate_uuid(product_id)

        stmt = (
            select(Product)
            .options(
                joinedload(Product.translations),
                selectinload(Product.tag_links),
            )
            .where(
                Product.product_id == product_id,
            )
        )

        result = await session.execute(stmt)
        product = result.unique().scalar()

        if not product:
            raise ProductNotFoundError(product_id)
        return product

    @classmethod
    async def search_products(
        cls,
        session: AsyncSession,
        category: str | None = None,
        sort_by: str | None = None,
        order: str | None = None,
        name: str | None = None,
        pagination_params: Pagination | None = None,
        query_only=False,
    ):
        """Search products with pagination, sorting, and filtering."""
        valid_sort_fields = ["name", "price", "category", "stock_quantity"]

        # Check if the sort_by field is valid
        if sort_by and sort_by not in valid_sort_fields:
            raise InvalidSortFieldError(
                f"'{sort_by}' is not a valid field for sorting."
            )

        # Define the order function
        if order and order not in ["asc", "desc"]:
            raise InvalidProductOrderError(order)

        order_func = desc if order == "desc" else asc

        translation_alias = aliased(ProductTranslation)

        # Subquery for translations with row_number to get the first translation for each product.
        translation_subquery = select(
            translation_alias.product_id,
            translation_alias.product_name,
            translation_alias.product_description,
            func.row_number()
            .over(
                partition_by=translation_alias.product_id,
                order_by=order_func(translation_alias.product_name),
            )
            .label("rank"),
        )

        # Filter by name if provided.
        if name:
            name = name.strip()
            translation_subquery = translation_subquery.where(
                translation_alias.product_name.ilike(f"%{name}%")
            )

        translation_subquery = translation_subquery.subquery()

        # Main query to get products and join with the first translation found for each product.
        stmt = (
            select(Product)
            .join(
                translation_subquery,
                translation_subquery.c.product_id == Product.product_id,
            )
            .where(
                translation_subquery.c.rank == 1
            )  # Get only the first matching translation
            .options(
                selectinload(Product.translations),
                selectinload(Product.tag_links),
            )  # Load all translations for each product
        )

        # Filter by category if provided.
        if category:
            stmt = stmt.where(Product.category == category)

        # Sorting based on selected field
        if sort_by:
            if sort_by == "name":
                # Sort using the subquery's product_name field
                sort_field = translation_subquery.c.product_name
            else:
                # Sort using Product's attributes directly
                sort_field = getattr(Product, sort_by)

            # Apply the order to the statement
            stmt = stmt.order_by(order_func(sort_field))
        else:
            # Default ordering by product_id
            stmt = stmt.order_by(Product.product_id)

        # Log the final SQL statement for debugging
        logger.debug(f"Executing SQL query: {stmt}")

        # Apply pagination if provided
        if pagination_params is not None:
            stmt = stmt.limit(pagination_params.per_page).offset(
                (pagination_params.page - 1) * pagination_params.per_page
            )

        # Return the query statement if only querying, else execute
        if query_only:
            return stmt

        result = await session.execute(stmt)
        products = result.scalars().all()

        # Log the retrieved products for debugging
        logger.debug(f"Retrieved products: {products}")

        return products

    @classmethod
    @memoize(ttl=60 * 60 * 24)
    async def get_searched_products_response(
        cls,
        session: AsyncSession,
        pagination_params: Pagination,
        category: str | None = None,
        sort_by: str | None = None,
        order: str | None = None,
        name: str | None = None,
        current_language: str = "en",
    ) -> ProductPaginatedResponse:

        products = await cls.search_products(
            session=session,
            category=category,
            sort_by=sort_by,
            order=order,
            name=name,
            pagination_params=pagination_params,
        )
        products_query = await cls.search_products(
            session=session,
            category=category,
            sort_by=sort_by,
            order=order,
            name=name,
            query_only=True,
        )

        num_of_pages = await cls.get_num_of_pages(
            session=session,
            per_page=pagination_params.per_page,
            stmt=products_query,
        )

        localized_products = await cls.localize_products_list(
            products=products, language=current_language
        )

        return ProductPaginatedResponse(pages=num_of_pages, products=localized_products)

    @classmethod
    async def create_product(
        cls, session: AsyncSession, product_in: ProductCreate
    ) -> Product:
        """Create a new product and ensure no duplicate names exist."""
        completed_translations = await complete_product_translations(
            product_in.translations
        )
        translation_names = []
        for translation in completed_translations:
            translation_names.append(translation.product_name)

        # Check for duplicates in the incoming request before querying the database
        if len(translation_names) != len(set(translation_names)):
            raise ProductNameDuplicationError("Duplicate product names in request")

        stmt = select(ProductTranslation).where(
            ProductTranslation.product_name.in_(translation_names)
        )
        result = await session.execute(stmt)
        if result.scalars().first():
            raise ProductNameDuplicationError(translation_names)

        translations = [
            ProductTranslation(**translation.model_dump())
            for translation in completed_translations
        ]

        product = Product(
            price=product_in.price,
            category=product_in.category,
            stock_quantity=product_in.stock_quantity,
            image_src=product_in.image_src,
            translations=translations,
        )
        product.tag_links = await cls._resolve_tags(session, product_in.tags)

        session.add(product)
        await session.commit()
        await cls.invalidate_products_cache()
        return product

    @classmethod
    async def bulk_create_product(
        cls,
        session: AsyncSession,
        products_in: ProductBulkCreate,
    ) -> ProductBulkCreate:

        translation_names = []
        for product in products_in.products:
            product.translations = await complete_product_translations(
                product.translations
            )
            for translation in product.translations:
                translation_names.append(translation.product_name)

        # Check for duplicates in the incoming request before querying the database
        if len(translation_names) != len(set(translation_names)):
            raise ProductNameDuplicationError("Duplicate product names in request")

        stmt = select(ProductTranslation).where(
            ProductTranslation.product_name.in_(translation_names)
        )

        result = await session.execute(stmt)
        existing_products = result.scalars().all()

        if existing_products:
            existing_names = [
                translation.product_name for translation in existing_products
            ]
            raise ProductNameDuplicationError(
                f"Products with names {existing_names} already exist."
            )

        products = []
        for product in products_in.products:
            translations = [
                ProductTranslation(**translation.model_dump())
                for translation in product.translations
            ]
            products.append(
                Product(
                    price=product.price,
                    category=product.category,
                    stock_quantity=product.stock_quantity,
                    image_src=product.image_src,
                    translations=translations,
                    tag_links=await cls._resolve_tags(session, product.tags),
                )
            )

        session.add_all(products)
        await session.commit()
        await cls.invalidate_products_cache()
        return products_in  # Return the created products as a list

    @classmethod
    async def update_product(
        cls,
        session: AsyncSession,
        product_id: uuid.UUID,
        product_update: ProductUpdate | ProductPartialUpdate,
        partial: bool = False,
    ) -> Product:
        from app.api.v1.cart.services import CartService

        """Update an existing product, raising an error if it doesn't exist."""
        product = await cls.get_product(session, product_id)
        if product_update.translations and not partial:
            product_update.translations = await complete_product_translations(
                product_update.translations
            )
        # Ensure all DB calls are awaited properly
        for name, value in product_update.model_dump(exclude_unset=partial).items():
            if name == "translations":
                for translation in product_update.translations:
                    existing_translation = next(
                        (
                            product_translation
                            for product_translation in product.translations
                            if product_translation.language_code
                            == translation.language_code
                        ),
                        None,
                    )
                    if existing_translation is None:
                        if partial and (
                            not translation.product_name
                            or not translation.product_description
                        ):
                            continue
                        product.translations.append(
                            ProductTranslation(
                                product_id=product_id,
                                **translation.model_dump(exclude_unset=partial),
                            )
                        )
                    else:
                        stmt = (
                            update(ProductTranslation)
                            .where(
                                and_(
                                    ProductTranslation.product_id == product_id,
                                    ProductTranslation.language_code
                                    == translation.language_code,
                                )
                            )
                            .values(**translation.model_dump(exclude_unset=partial))
                        )
                        await session.execute(stmt)
            elif name == "tags":
                await cls._sync_product_tags(session, product, value)
            else:
                setattr(product, name, value)
        await session.commit()

        await CartService.update_cart_products_info(products=[product])
        await cls.invalidate_products_cache()
        return product

    @classmethod
    async def delete_product(
        cls,
        session: AsyncSession,
        product_id: uuid.UUID,
    ) -> None:
        """Delete a product by its ID. Perform soft deletion by default."""
        from app.api.v1.cart.services import CartService

        await cls.get_product(session, product_id)  # checking for product's existence
        await session.execute(delete(Product).where(Product.product_id == product_id))

        await session.commit()
        await CartService.remove_cart_item_references([product_id])
        await cls.invalidate_products_cache()

    @classmethod
    async def delete_products(
        cls,
        session: AsyncSession,
        product_ids: list[uuid.UUID],
    ) -> None:
        from app.api.v1.cart.services import CartService

        """Delete a product by its ID. Perform soft deletion by default."""
        await session.execute(
            delete(Product).where(Product.product_id.in_(product_ids))
        )
        await CartService.remove_cart_item_references(product_ids)

        await session.commit()
        await cls.invalidate_products_cache()

    @classmethod
    @memoize(ttl=300)
    async def get_similar_products_response(
        cls,
        session: AsyncSession,
        product_ids: list[uuid.UUID],
        current_language: str = "en",
        limit: int = 4,
    ) -> list[ProductResponse]:
        source_ids = list(dict.fromkeys(product_ids))
        if not source_ids:
            return []

        source_result = await session.execute(
            select(Product)
            .options(selectinload(Product.tag_links))
            .where(Product.product_id.in_(source_ids))
        )
        source_products = source_result.scalars().all()
        source_tags = {tag for product in source_products for tag in product.tags}
        source_categories = {
            product.category
            for product in source_products
            if product.category
        }
        if not source_tags and not source_categories:
            return []

        candidate_result = await session.execute(
            select(Product)
            .options(
                selectinload(Product.translations),
                selectinload(Product.tag_links),
            )
            .where(Product.product_id.notin_(source_ids))
        )
        candidates = candidate_result.scalars().all()
        scored: list[tuple[int, str, Product]] = []
        for product in candidates:
            shared_tags = source_tags.intersection(product.tags)
            category_match = bool(product.category in source_categories)
            score = len(shared_tags) * 10 + (2 if category_match else 0)
            if score > 0:
                scored.append((score, product.category or "", product))

        scored.sort(key=lambda row: (-row[0], row[1], str(row[2].product_id)))
        return await cls.localize_products_list(
            [product for _, _, product in scored[:limit]],
            current_language,
        )

    @classmethod
    async def invalidate_products_cache(cls):
        if redis_db_helper.cache is None:
            return

        for m in [
            cls.get_all_products_response,
            cls.get_product,
            cls.get_searched_products_response,
            cls.get_similar_products_response,
        ]:

            await redis_db_helper.cache.invalidate(m, invalidate_all=True)
