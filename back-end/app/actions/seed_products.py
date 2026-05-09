from app.actions.migrate_all_database import (
    PRODUCTS_DATA,
    ProductSeedResult,
    main,
    seed_products,
)

__all__ = (
    "PRODUCTS_DATA",
    "ProductSeedResult",
    "main",
    "seed_products",
)


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="Seed catalog products safely.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate only known seed products. Local use only.",
    )
    args = parser.parse_args()
    asyncio.run(main(reset=args.reset))
