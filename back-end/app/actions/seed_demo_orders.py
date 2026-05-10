from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.api.v1.products.services import ProductsService
from app.core import helpers
from app.core.models import (
    Address,
    City,
    Country,
    Order,
    OrderProductAssociation,
    Product,
    State,
    sql_db_helper,
)

@dataclass(frozen=True)
class DemoOrderSeedResult:
    created: int
    skipped: int


DEMO_ORDER_BLUEPRINTS = [
    {
        "email": "demo.customer.01@local.cheburek-shop.com",
        "status": "DELIVERED",
        "products": [("Cheburek with meat", 2), ("Coca-Cola 0.5L", 1)],
        "days_ago": 13,
        "notes": "Leave at reception.",
    },
    {
        "email": "demo.customer.02@local.cheburek-shop.com",
        "status": "READY",
        "products": [("Pie with potatoes", 3), ("Sprite 0.5L", 2)],
        "days_ago": 11,
        "notes": "Please add extra napkins.",
    },
    {
        "email": "demo.customer.03@local.cheburek-shop.com",
        "status": "PREPARING",
        "products": [("Cheburek with chicken and cheese", 2)],
        "days_ago": 8,
        "notes": None,
    },
    {
        "email": "demo.customer.04@local.cheburek-shop.com",
        "status": "CONFIRMED",
        "products": [("Pie with cheese and herbs", 4), ("French fries", 2)],
        "days_ago": 6,
        "notes": "Call before delivery.",
    },
    {
        "email": "demo.customer.05@local.cheburek-shop.com",
        "status": "PENDING",
        "products": [("Cheburek with meat and cheese", 1), ("Nuggets", 2)],
        "days_ago": 3,
        "notes": None,
    },
    {
        "email": "demo.customer.06@local.cheburek-shop.com",
        "status": "CANCELLED",
        "products": [("Pie with cabbage", 2)],
        "days_ago": 2,
        "notes": "Customer requested cancellation.",
    },
    {
        "email": "demo.customer.07@local.cheburek-shop.com",
        "status": "DELIVERED",
        "products": [
            ("Cheburek with chicken, cheese, and mushrooms", 2),
            ("Sprite 0.5L", 1),
        ],
        "days_ago": 1,
        "notes": None,
    },
]


DEMO_PRODUCT_MIX = [
    [("Cheburek with meat", 2), ("Coca-Cola 0.5L", 1)],
    [("Cheburek with chicken", 1), ("Sprite 0.5L", 1)],
    [("Cheburek with meat and cheese", 2), ("French fries", 1)],
    [("Cheburek with chicken and cheese", 2), ("Nuggets", 1)],
    [("Cheburek with chicken, cheese, and mushrooms", 1), ("Sprite 0.5L", 2)],
    [("Cheburek with meat, cheese, and mushrooms", 1), ("Coca-Cola 0.5L", 1)],
    [("Pie with potatoes", 3), ("Coca-Cola 0.5L", 1)],
    [("Pie with cabbage", 4), ("Sprite 0.5L", 1)],
    [("Pie with cheese and herbs", 3), ("French fries", 1)],
    [("Pie with potatoes and mushrooms", 2), ("Nuggets", 2)],
]

DEMO_STATUSES = [
    "DELIVERED",
    "DELIVERED",
    "DELIVERED",
    "READY",
    "PREPARING",
    "CONFIRMED",
    "PENDING",
    "CANCELLED",
]

DEMO_NOTES = [
    "Leave at reception.",
    "Please add extra napkins.",
    "Call before delivery.",
    "No onions in sauces.",
    "Pack drinks separately.",
    None,
]


def build_demo_order_blueprints() -> list[dict]:
    blueprints: list[dict] = []
    for index in range(45):
        day_offset = 44 - index
        status = DEMO_STATUSES[index % len(DEMO_STATUSES)]
        product_mix = DEMO_PRODUCT_MIX[index % len(DEMO_PRODUCT_MIX)]
        quantity_boost = 1 if index % 9 == 0 else 0
        products = [
            (product_name, quantity + quantity_boost)
            for product_name, quantity in product_mix
        ]
        blueprints.append(
            {
                "email": f"demo.customer.{index + 1:02d}@local.cheburek-shop.com",
                "status": status,
                "products": products,
                "days_ago": day_offset,
                "notes": DEMO_NOTES[index % len(DEMO_NOTES)],
            }
        )
    return blueprints


async def _products_by_name(session) -> dict[str, Product]:
    result = await session.execute(
        select(Product)
        .options(
            selectinload(Product.translations),
            selectinload(Product.tag_links),
        )
    )
    products = result.scalars().all()
    indexed: dict[str, Product] = {}
    for product in products:
        for translation in product.translations:
            if translation.language_code == "en":
                indexed[translation.product_name] = product
                break
    return indexed


async def _create_address(session, index: int) -> Address:
    country = await helpers.get_or_create(
        session=session,
        model=Country,
        country_name="ukraine",
    )
    await session.flush()
    state = await helpers.get_or_create(
        session=session,
        model=State,
        state_name="lviv oblast",
        country_id=country.country_id,
    )
    await session.flush()
    city = await helpers.get_or_create(
        session=session,
        model=City,
        city_name="lviv",
        state_id=state.state_id,
    )
    await session.flush()
    address = Address(
        street_name="Local Demo Street",
        street_number=str(10 + index),
        apartment_number=str(index),
        zip_code="79000",
        city_id=city.city_id,
    )
    session.add(address)
    await session.flush()
    return address


async def seed_demo_orders(session=None) -> DemoOrderSeedResult:
    owns_session = session is None
    if owns_session:
        session_context = sql_db_helper.session_factory()
        session = await session_context.__aenter__()
    else:
        session_context = None

    try:
        blueprints = build_demo_order_blueprints()
        emails = [blueprint["email"] for blueprint in blueprints]
        existing_result = await session.execute(
            select(Order).where(Order.email.in_(emails))
        )
        existing_orders = {
            order.email: order
            for order in existing_result.scalars().all()
        }
        products_by_name = await _products_by_name(session)

        created = 0
        skipped = 0
        for index, blueprint in enumerate(blueprints, start=1):
            total_count = 0
            total_price = 0.0
            associations: list[OrderProductAssociation] = []
            order_id = (
                existing_orders[blueprint["email"]].order_id
                if blueprint["email"] in existing_orders
                else uuid.uuid4()
            )
            for product_name, quantity in blueprint["products"]:
                product = products_by_name.get(product_name)
                if product is None:
                    continue
                localized = await ProductsService.localize_product(product, "en")
                associations.append(
                    OrderProductAssociation(
                        order_id=order_id,
                        product_id=product.product_id,
                        quantity=quantity,
                        name=localized.name,
                        price=product.price,
                        category=product.category,
                        image_src=product.image_src,
                    )
                )
                total_count += quantity
                total_price += product.price * quantity

            if not associations:
                skipped += 1
                continue

            if blueprint["email"] in existing_orders:
                order = existing_orders[blueprint["email"]]
                await session.execute(
                    delete(OrderProductAssociation).where(
                        OrderProductAssociation.order_id == order.order_id
                    )
                )
                skipped += 1
            else:
                address = await _create_address(session, index)
                order = Order(order_id=order_id, address_id=address.address_id)
                session.add(order)
                created += 1

            order.created_at = datetime.now() - timedelta(days=blueprint["days_ago"])
            order.email = blueprint["email"]
            order.status = blueprint["status"]
            order.customer_notes = blueprint["notes"]
            order.admin_notes = (
                "Demo fulfillment note."
                if blueprint["status"] in {"READY", "DELIVERED"}
                else None
            )
            order.total_count = total_count
            order.total_price = total_price
            session.add(order)
            session.add_all(associations)

        await session.commit()
        return DemoOrderSeedResult(created=created, skipped=skipped)
    except Exception:
        await session.rollback()
        raise
    finally:
        if owns_session and session_context is not None:
            await session_context.__aexit__(None, None, None)


async def main() -> None:
    result = await seed_demo_orders()
    print(
        "Demo order seed complete: "
        f"created={result.created}, skipped={result.skipped}"
    )
    await sql_db_helper.dispose()


if __name__ == "__main__":
    asyncio.run(main())
