import asyncio

from app.core.models import mongo_db_helper, redis_db_helper, sql_db_helper
from app.core.services.product_translations import backfill_product_translations


async def main() -> None:
    await mongo_db_helper.connect()
    await redis_db_helper.connect()
    try:
        async with sql_db_helper.session_factory() as session:
            result = await backfill_product_translations(session=session)
            print(
                "Product translation backfill complete: "
                f"products_scanned={result.products_scanned}, "
                f"translations_created={result.translations_created}"
            )
    finally:
        await mongo_db_helper.dispose()
        await redis_db_helper.dispose()
        await sql_db_helper.dispose()


if __name__ == "__main__":
    asyncio.run(main())
