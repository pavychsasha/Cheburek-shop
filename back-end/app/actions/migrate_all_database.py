import asyncio
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.core.models import Product, redis_db_helper, sql_db_helper
from app.core.models.product_translations import (
    ProductTranslation as ProductTranslationModel,
)
from app.core.schemas.products import ProductBulkCreate

# Data to be used for bulk creation
PRODUCTS_DATA = {
    "products": [
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Cheburek with meat",
                    "product_description": "Cheburek with delicious meat",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Чебурек із м'ясом",
                    "product_description": "Чебурек із смачним м'ясом",
                },
            ],
            "price": 55,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Cheburek with chicken, cheese, and mushrooms",
                    "product_description": "Cheburek with chicken, cheese, and mushrooms",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Чебурек із куркою, сиром та грибами",
                    "product_description": "Чебурек із куркою, сиром та грибами",
                },
            ],
            "price": 65,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Nuggets",
                    "product_description": "Juicy nuggets",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Нагетси",
                    "product_description": "Соковиті нагетси",
                },
            ],
            "price": 25,
            "category": "Other",
            "stock_quantity": 150,
            "image_src": "https://i.imgur.com/UAYLcz3.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Pie with cheese and herbs",
                    "product_description": "Pie with cheese and herbs",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Пиріжок з сиром та зеленню",
                    "product_description": "Пиріжок з сиром та зеленню",
                },
            ],
            "price": 20,
            "category": "Pies",
            "stock_quantity": 200,
            "image_src": "https://i.imgur.com/gcIZ0Es.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Cheburek with meat and cheese",
                    "product_description": "Cheburek with meat and cheese",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Чебурек із м'ясом та сиром",
                    "product_description": "Чебурек із м'ясом та сиром",
                },
            ],
            "price": 60,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Cheburek with meat, cheese, and mushrooms",
                    "product_description": "Cheburek with meat, cheese, and mushrooms",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Чебурек із м'ясом, сиром та грибами",
                    "product_description": "Чебурек із м'ясом, сиром та грибами",
                },
            ],
            "price": 65,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Pie with potatoes",
                    "product_description": "Pie with tender potatoes",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Пиріжок з картоплею",
                    "product_description": "Пиріжок з ніжною картоплею",
                },
            ],
            "price": 20,
            "category": "Pies",
            "stock_quantity": 200,
            "image_src": "https://i.imgur.com/gcIZ0Es.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Cheburek with chicken",
                    "product_description": "Cheburek with juicy chicken",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Чебурек із куркою",
                    "product_description": "Чебурек із соковитою куркою",
                },
            ],
            "price": 55,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "French fries",
                    "product_description": "Crispy French fries",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Картопля фрі",
                    "product_description": "Хрустка картопля фрі",
                },
            ],
            "price": 20,
            "category": "Other",
            "stock_quantity": 150,
            "image_src": "https://i.imgur.com/I8VYekg.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Pie with potatoes and mushrooms",
                    "product_description": "Pie with potatoes and mushrooms",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Пиріжок з картоплею та грибами",
                    "product_description": "Пиріжок з картоплею та грибами",
                },
            ],
            "price": 25,
            "category": "Pies",
            "stock_quantity": 200,
            "image_src": "https://i.imgur.com/gcIZ0Es.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Coca-Cola 0.5L",
                    "product_description": "Refreshing Coca-Cola 0.5L drink",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Кока-кола 0.5л",
                    "product_description": "Освіжаючий напій Кока-кола 0.5л",
                },
            ],
            "price": 30,
            "category": "Drinks",
            "stock_quantity": 300,
            "image_src": "https://i.imgur.com/ym0F0Lg.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Cheburek with chicken and cheese",
                    "product_description": "Cheburek with chicken and cheese",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Чебурек із куркою та сиром",
                    "product_description": "Чебурек із куркою та сиром",
                },
            ],
            "price": 60,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Pie with cabbage",
                    "product_description": "Pie with cabbage",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Пиріжок з капустою",
                    "product_description": "Пиріжок з капустою",
                },
            ],
            "price": 18,
            "category": "Pies",
            "stock_quantity": 200,
            "image_src": "https://i.imgur.com/gcIZ0Es.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Sprite 0.5L",
                    "product_description": "Refreshing Sprite 0.5L drink",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Спрайт 0.5л",
                    "product_description": "Освіжаючий напій Спрайт 0.5л",
                },
            ],
            "price": 30,
            "category": "Drinks",
            "stock_quantity": 300,
            "image_src": "https://i.imgur.com/l7RFgRd.png",
        },
    ]
}


@dataclass(frozen=True)
class ProductSeedResult:
    created: int
    updated: int
    skipped: int
    reset: bool
    total_seed_products: int


def _seed_products() -> ProductBulkCreate:
    products_in = ProductBulkCreate(**PRODUCTS_DATA)
    names = [_english_name(product) for product in products_in.products]
    if len(names) != len(set(names)):
        raise ValueError("Seed products must have unique English names.")
    return products_in


def _english_name(product) -> str:
    for translation in product.translations:
        if translation.language_code == "en":
            return translation.product_name
    raise ValueError("Each seed product must include an English translation.")


async def _get_existing_seed_products(
    session, seed_names: list[str]
) -> dict[str, Product]:
    stmt = (
        select(Product)
        .join(Product.translations)
        .options(joinedload(Product.translations))
        .where(
            ProductTranslationModel.language_code == "en",
            ProductTranslationModel.product_name.in_(seed_names),
        )
    )
    result = await session.execute(stmt)
    products = result.unique().scalars().all()

    products_by_seed_name: dict[str, Product] = {}
    for product in products:
        for translation in product.translations:
            if (
                translation.language_code == "en"
                and translation.product_name in seed_names
            ):
                products_by_seed_name[translation.product_name] = product
                break
    return products_by_seed_name


def _apply_seed_product(existing_product: Product, seed_product) -> bool:
    changed = False
    scalar_fields = ("price", "category", "stock_quantity", "image_src")

    for field_name in scalar_fields:
        new_value = getattr(seed_product, field_name)
        if getattr(existing_product, field_name) != new_value:
            setattr(existing_product, field_name, new_value)
            changed = True

    translations_by_language = {
        translation.language_code: translation
        for translation in existing_product.translations
    }
    for seed_translation in seed_product.translations:
        existing_translation = translations_by_language.get(
            seed_translation.language_code
        )
        if existing_translation is None:
            existing_product.translations.append(
                ProductTranslationModel(**seed_translation.model_dump())
            )
            changed = True
            continue

        for field_name in ("product_name", "product_description"):
            new_value = getattr(seed_translation, field_name)
            if getattr(existing_translation, field_name) != new_value:
                setattr(existing_translation, field_name, new_value)
                changed = True

    return changed


async def _delete_seed_products(session, seed_names: list[str]) -> int:
    products_by_seed_name = await _get_existing_seed_products(session, seed_names)
    product_ids = [product.product_id for product in products_by_seed_name.values()]
    if not product_ids:
        return 0

    await session.execute(delete(Product).where(Product.product_id.in_(product_ids)))
    await session.flush()
    return len(product_ids)


async def seed_products(session=None, *, reset: bool = False) -> ProductSeedResult:
    products_in = _seed_products()
    seed_names = [_english_name(product) for product in products_in.products]
    owns_session = session is None

    if owns_session:
        session_context = sql_db_helper.session_factory()
        session = await session_context.__aenter__()
    else:
        session_context = None

    try:
        if reset:
            await _delete_seed_products(session, seed_names)

        existing_products = await _get_existing_seed_products(session, seed_names)
        created = 0
        updated = 0
        skipped = 0

        for seed_product in products_in.products:
            seed_name = _english_name(seed_product)
            existing_product = existing_products.get(seed_name)
            if existing_product is None:
                translations = [
                    ProductTranslationModel(**translation.model_dump())
                    for translation in seed_product.translations
                ]
                session.add(
                    Product(
                        price=seed_product.price,
                        category=seed_product.category,
                        stock_quantity=seed_product.stock_quantity,
                        image_src=seed_product.image_src,
                        translations=translations,
                    )
                )
                created += 1
                continue

            if _apply_seed_product(existing_product, seed_product):
                session.add(existing_product)
                updated += 1
            else:
                skipped += 1

        await session.commit()
        if redis_db_helper.cache is not None:
            await redis_db_helper.cache.remove_all_cache_keys()

        return ProductSeedResult(
            created=created,
            updated=updated,
            skipped=skipped,
            reset=reset,
            total_seed_products=len(products_in.products),
        )
    except Exception:
        await session.rollback()
        raise
    finally:
        if owns_session and session_context is not None:
            await session_context.__aexit__(None, None, None)


async def main(reset: bool = False):
    await redis_db_helper.connect()
    try:
        result = await seed_products(reset=reset)
        print(
            "Product seed complete: "
            f"created={result.created}, "
            f"updated={result.updated}, "
            f"skipped={result.skipped}, "
            f"reset={result.reset}"
        )
    finally:
        await redis_db_helper.dispose()
        await sql_db_helper.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed catalog products safely.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate only known seed products. Local use only.",
    )
    args = parser.parse_args()
    asyncio.run(main(reset=args.reset))
