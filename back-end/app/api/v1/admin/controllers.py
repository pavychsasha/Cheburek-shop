from typing import Annotated

from fastapi import APIRouter, Depends, File, Security, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.seed_products import seed_products
from app.core.dependencies.authentication.fastapi_users_dependency import (
    current_active_superuser,
)
from app.core.models import (
    Order,
    OrderProductAssociation,
    Product,
    User,
    sql_db_helper,
)
from app.core.models.product_translations import ProductTranslation
from app.core.schemas.admin import (
    AdminAnalytics,
    DashboardPreferences,
    AdminSummary,
    LowStockProduct,
    ProductSeedResponse,
    RecentOrder,
    StatusCount,
    TimeSeriesPoint,
    TopProduct,
)
from app.core.services.dashboard_preferences import (
    get_dashboard_preferences,
    update_dashboard_preferences,
)
from app.core.schemas.settings import (
    CurrencySettings,
    CurrencySettingsUpdate,
    MediaUploadResponse,
    ProductLanguageSettings,
    ProductLanguageSettingsUpdate,
    ProductTranslationBackfillResponse,
)
from app.core.services.product_translations import backfill_product_translations
from app.core.services.store_settings import (
    update_currency_settings,
    update_product_language_settings,
)
from app.core.services.visitor_analytics import (
    get_today_page_views,
    get_today_unique_visitors,
    get_visitor_time_series,
)
from app.core.storage import upload_product_image

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
    unique_visitors_today = await get_today_unique_visitors(session)
    page_views_today = await get_today_page_views(session)

    return AdminSummary(
        products_count=products_count or 0,
        orders_count=orders_count or 0,
        users_count=users_count or 0,
        low_stock_products_count=low_stock_products_count or 0,
        pending_orders_count=pending_orders_count or 0,
        unique_visitors_today=unique_visitors_today,
        page_views_today=page_views_today,
    )


@router.get(
    "/analytics",
    response_model=AdminAnalytics,
    status_code=status.HTTP_200_OK,
)
async def get_admin_analytics(
    session: Annotated[
        AsyncSession,
        Depends(sql_db_helper.session_dependency),
    ],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    status_rows = (
        await session.execute(
            select(Order.status, func.count(Order.order_id))
            .group_by(Order.status)
            .order_by(Order.status)
        )
    ).all()

    date_bucket = func.date(Order.created_at)
    order_time_rows = (
        await session.execute(
            select(date_bucket, func.count(Order.order_id))
            .group_by(date_bucket)
            .order_by(date_bucket.desc())
            .limit(14)
        )
    ).all()
    revenue_time_rows = (
        await session.execute(
            select(date_bucket, func.coalesce(func.sum(Order.total_price), 0))
            .group_by(date_bucket)
            .order_by(date_bucket.desc())
            .limit(14)
        )
    ).all()
    visitors_over_time, page_views_over_time = await get_visitor_time_series(
        session,
        days=14,
    )

    low_stock_rows = (
        await session.execute(
            select(
                Product.product_id,
                ProductTranslation.product_name,
                Product.stock_quantity,
            )
            .join(Product.translations)
            .where(ProductTranslation.language_code == "en")
            .order_by(Product.stock_quantity.asc(), ProductTranslation.product_name)
            .limit(8)
        )
    ).all()

    top_product_rows = (
        await session.execute(
            select(
                OrderProductAssociation.name,
                func.coalesce(func.sum(OrderProductAssociation.quantity), 0),
                func.coalesce(
                    func.sum(
                        OrderProductAssociation.price
                        * OrderProductAssociation.quantity
                    ),
                    0,
                ),
            )
            .group_by(OrderProductAssociation.name)
            .order_by(
                func.coalesce(func.sum(OrderProductAssociation.quantity), 0).desc()
            )
            .limit(8)
        )
    ).all()

    recent_order_rows = (
        await session.execute(
            select(Order)
            .order_by(Order.created_at.desc())
            .limit(8)
        )
    )

    return AdminAnalytics(
        orders_by_status=[
            StatusCount(status=row[0], count=row[1] or 0)
            for row in status_rows
        ],
        orders_over_time=[
            TimeSeriesPoint(date=row[0], value=float(row[1] or 0))
            for row in reversed(order_time_rows)
        ],
        revenue_over_time=[
            TimeSeriesPoint(date=row[0], value=float(row[1] or 0))
            for row in reversed(revenue_time_rows)
        ],
        visitors_over_time=visitors_over_time,
        page_views_over_time=page_views_over_time,
        low_stock_products=[
            LowStockProduct(
                product_id=row[0],
                name=row[1],
                stock_quantity=row[2] or 0,
            )
            for row in low_stock_rows
        ],
        top_products=[
            TopProduct(
                name=row[0],
                quantity=row[1] or 0,
                revenue=float(row[2] or 0),
            )
            for row in top_product_rows
        ],
        recent_orders=[
            RecentOrder(
                order_id=order.order_id,
                created_at=order.created_at,
                status=order.status,
                email=order.email,
                total_price=order.total_price,
                total_count=order.total_count,
            )
            for order in recent_order_rows.scalars().all()
        ],
    )


@router.get(
    "/dashboard/preferences",
    response_model=DashboardPreferences,
    status_code=status.HTTP_200_OK,
)
async def get_admin_dashboard_preferences(
    session: Annotated[
        AsyncSession,
        Depends(sql_db_helper.session_dependency),
    ],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await get_dashboard_preferences(
        session=session,
        user_id=superuser.id,
    )


@router.patch(
    "/dashboard/preferences",
    response_model=DashboardPreferences,
    status_code=status.HTTP_200_OK,
)
async def update_admin_dashboard_preferences(
    preferences: DashboardPreferences,
    session: Annotated[
        AsyncSession,
        Depends(sql_db_helper.session_dependency),
    ],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await update_dashboard_preferences(
        session=session,
        user_id=superuser.id,
        update=preferences,
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


@router.patch(
    "/settings/currency",
    response_model=CurrencySettings,
    status_code=status.HTTP_200_OK,
)
async def update_admin_currency_settings(
    currency_settings: CurrencySettingsUpdate,
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await update_currency_settings(currency_settings)


@router.patch(
    "/settings/languages",
    response_model=ProductLanguageSettings,
    status_code=status.HTTP_200_OK,
)
async def update_admin_language_settings(
    language_settings: ProductLanguageSettingsUpdate,
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await update_product_language_settings(language_settings)


@router.post(
    "/translations/backfill",
    response_model=ProductTranslationBackfillResponse,
    status_code=status.HTTP_200_OK,
)
async def backfill_admin_product_translations(
    session: Annotated[
        AsyncSession,
        Depends(sql_db_helper.session_dependency),
    ],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await backfill_product_translations(session=session)


@router.post(
    "/media/products",
    response_model=MediaUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_admin_product_media(
    superuser: Annotated[User, Security(current_active_superuser)],
    file: UploadFile = File(...),
):
    stored_object = await upload_product_image(file)
    return MediaUploadResponse(
        object_name=stored_object.object_name,
        url=stored_object.url,
        content_type=stored_object.content_type,
        size=stored_object.size,
    )
