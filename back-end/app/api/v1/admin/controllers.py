from typing import Annotated

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.seed_products import seed_products
from app.core.dependencies.authentication.fastapi_users_dependency import (
    current_active_superuser,
)
from app.core.models import Order, Product, User, sql_db_helper
from app.core.schemas.admin import AdminSummary, ProductSeedResponse

router = APIRouter(tags=["Admin"])


@router.get(
    "/summary",
    response_model=AdminSummary,
    status_code=status.HTTP_200_OK,
)
async def get_admin_summary(
    session: Annotated[
        AsyncSession,
        Depends(sql_db_helper.session_dependency),
    ],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    products_count = await session.scalar(
        select(func.count()).select_from(Product)
    )
    orders_count = await session.scalar(
        select(func.count()).select_from(Order)
    )
    users_count = await session.scalar(select(func.count()).select_from(User))
    low_stock_products_count = await session.scalar(
        select(func.count())
        .select_from(Product)
        .where(Product.stock_quantity <= 10)
    )
    pending_orders_count = await session.scalar(
        select(func.count())
        .select_from(Order)
        .where(Order.status == "PENDING")
    )

    return AdminSummary(
        products_count=products_count or 0,
        orders_count=orders_count or 0,
        users_count=users_count or 0,
        low_stock_products_count=low_stock_products_count or 0,
        pending_orders_count=pending_orders_count or 0,
    )


@router.post(
    "/seed/products",
    response_model=ProductSeedResponse,
    status_code=status.HTTP_200_OK,
)
async def seed_catalog_products(
    session: Annotated[
        AsyncSession,
        Depends(sql_db_helper.session_dependency),
    ],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    result = await seed_products(session=session)
    return ProductSeedResponse(
        created=result.created,
        updated=result.updated,
        skipped=result.skipped,
        reset=result.reset,
        total_seed_products=result.total_seed_products,
    )
