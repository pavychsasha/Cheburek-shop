import asyncio

from sqlalchemy import text, inspect

from app.core.models import sql_db_helper
from app.api.v1.products.services import bulk_create_product, ProductBulkCreate
from alembic.config import Config
from alembic import command

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

# Paths for Alembic configuration
ALEMBIC_CONFIG_PATH = (
    "alembic.ini"  # Update if your alembic config is in a different path
)


async def truncate_products_databases():
    # Implement truncation logic for your databases here
    # If using SQLAlchemy, you could drop and recreate tables or run raw SQL commands.
    async with sql_db_helper.session_factory() as session:
        async with session.bind.connect() as conn:
            # Use run_sync to execute a synchronous function with the connection
            def sync_inspect(connection):
                inspector = inspect(connection)
                return inspector.get_table_names()

            tables = await conn.run_sync(sync_inspect)
            print("Available tables in the database:", tables)

        await session.execute(text('TRUNCATE TABLE "Products" CASCADE;'))
        await session.execute(text('TRUNCATE TABLE "Orders" CASCADE;'))
        await session.commit()
    print("All databases truncated.")


def upgrade_alembic():
    print("Upgrading Alembic...")
    alembic_cfg = Config(ALEMBIC_CONFIG_PATH)
    command.upgrade(alembic_cfg, "head")
    print("Alembic upgraded to head.")


async def run_bulk_create():
    async with sql_db_helper.session_factory() as session:
        products_in = ProductBulkCreate(**PRODUCTS_DATA)
        result = await bulk_create_product(session, products_in)
        print(f"Bulk creation of products completed: {result}")


async def main():
    # Truncate databases
    await truncate_products_databases()

    # Upgrade Alembic
    upgrade_alembic()

    # Run bulk create
    await run_bulk_create()


if __name__ == "__main__":
    asyncio.run(main())
