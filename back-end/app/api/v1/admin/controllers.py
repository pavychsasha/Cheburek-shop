from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Query, Security, UploadFile, status
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
    ProfitSettings,
    ProfitSettingsUpdate,
    ProductTranslationBackfillResponse,
    ProductTranslationPreviewRequest,
    ProductTranslationPreviewResponse,
    ProductTranslationPreviewItem,
)
from app.core.services.product_translations import (
    backfill_product_translations,
    preview_product_translations,
)
from app.core.services.store_settings import (
    get_profit_settings,
    update_profit_settings,
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


def _period_bucket(value: datetime, period: str) -> date:
    current = value.date()
    if period == "week":
        return current - timedelta(days=current.weekday())
    if period == "month":
        return current.replace(day=1)
    return current


def _empty_profit_metrics() -> dict[str, float]:
    return {
        "total_revenue": 0.0,
        "total_recorded_cost": 0.0,
        "gross_profit": 0.0,
        "estimated_profit": 0.0,
        "profit_margin_percent": 0.0,
        "average_order_value": 0.0,
    }


async def _profit_metrics(
    session: AsyncSession,
    *,
    fallback_margin: float,
    since: datetime | None = None,
) -> dict[str, float]:
    stmt = select(
        Order.order_id,
        OrderProductAssociation.price,
        OrderProductAssociation.cost_price,
        OrderProductAssociation.quantity,
    ).join(
        OrderProductAssociation,
        OrderProductAssociation.order_id == Order.order_id,
    )
    if since is not None:
        stmt = stmt.where(Order.created_at >= since)

    rows = (await session.execute(stmt)).all()
    if not rows:
        return _empty_profit_metrics()

    revenue = 0.0
    recorded_cost = 0.0
    actual_profit = 0.0
    estimated_profit = 0.0
    order_ids: set = set()
    for order_id, price, cost_price, quantity in rows:
        line_revenue = float(price or 0) * int(quantity or 0)
        line_cost = float(cost_price or 0) * int(quantity or 0)
        revenue += line_revenue
        recorded_cost += line_cost
        order_ids.add(order_id)
        if line_cost > 0:
            actual_profit += line_revenue - line_cost
            estimated_profit += line_revenue - line_cost
        else:
            estimated_profit += line_revenue * fallback_margin

    return {
        "total_revenue": round(revenue, 2),
        "total_recorded_cost": round(recorded_cost, 2),
        "gross_profit": round(actual_profit, 2),
        "estimated_profit": round(estimated_profit, 2),
        "profit_margin_percent": round(
            (estimated_profit / revenue * 100) if revenue else 0,
            2,
        ),
        "average_order_value": round(
            revenue / len(order_ids) if order_ids else 0,
            2,
        ),
    }


async def _analytics_series(
    session: AsyncSession,
    *,
    fallback_margin: float,
    since: datetime,
    period: str,
) -> dict[str, list[TimeSeriesPoint]]:
    rows = (
        await session.execute(
            select(
                Order.created_at,
                OrderProductAssociation.price,
                OrderProductAssociation.cost_price,
                OrderProductAssociation.quantity,
            )
            .join(
                OrderProductAssociation,
                OrderProductAssociation.order_id == Order.order_id,
            )
            .where(Order.created_at >= since)
            .order_by(Order.created_at)
        )
    ).all()

    buckets: dict[date, dict[str, float]] = defaultdict(
        lambda: {"revenue": 0.0, "cost": 0.0, "profit": 0.0}
    )
    for created_at, price, cost_price, quantity in rows:
        bucket = _period_bucket(created_at, period)
        line_revenue = float(price or 0) * int(quantity or 0)
        line_cost = float(cost_price or 0) * int(quantity or 0)
        buckets[bucket]["revenue"] += line_revenue
        buckets[bucket]["cost"] += line_cost
        buckets[bucket]["profit"] += (
            line_revenue - line_cost
            if line_cost > 0
            else line_revenue * fallback_margin
        )

    ordered = sorted(buckets.items(), key=lambda item: item[0])
    return {
        "revenue_over_time": [
            TimeSeriesPoint(date=bucket, value=round(values["revenue"], 2))
            for bucket, values in ordered
        ],
        "cost_over_time": [
            TimeSeriesPoint(date=bucket, value=round(values["cost"], 2))
            for bucket, values in ordered
        ],
        "profit_over_time": [
            TimeSeriesPoint(date=bucket, value=round(values["profit"], 2))
            for bucket, values in ordered
        ],
    }


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
    profit_settings = await get_profit_settings()
    profit_metrics = await _profit_metrics(
        session,
        fallback_margin=profit_settings.fallback_profit_margin,
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
        **profit_metrics,
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
    timespan_days: Annotated[int, Query(ge=1, le=365)] = 30,
    period: Annotated[Literal["day", "week", "month"], Query()] = "day",
):
    since = datetime.now() - timedelta(days=timespan_days)
    profit_settings = await get_profit_settings()
    fallback_margin = profit_settings.fallback_profit_margin

    status_rows = (
        await session.execute(
            select(Order.status, func.count(Order.order_id))
            .where(Order.created_at >= since)
            .group_by(Order.status)
            .order_by(Order.status)
        )
    ).all()

    order_rows = (
        await session.execute(
            select(Order.created_at)
            .where(Order.created_at >= since)
            .order_by(Order.created_at)
        )
    ).all()
    order_buckets: dict[date, int] = defaultdict(int)
    for row in order_rows:
        order_buckets[_period_bucket(row[0], period)] += 1
    orders_over_time = [
        TimeSeriesPoint(date=bucket, value=float(count))
        for bucket, count in sorted(order_buckets.items(), key=lambda item: item[0])
    ]

    series = await _analytics_series(
        session,
        fallback_margin=fallback_margin,
        since=since,
        period=period,
    )
    visitors_over_time, page_views_over_time = await get_visitor_time_series(
        session,
        days=timespan_days,
    )
    profit_metrics = await _profit_metrics(
        session,
        fallback_margin=fallback_margin,
        since=since,
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
                func.coalesce(
                    func.sum(
                        (
                            OrderProductAssociation.price
                            - OrderProductAssociation.cost_price
                        )
                        * OrderProductAssociation.quantity
                    ),
                    0,
                ),
            )
            .join(Order, Order.order_id == OrderProductAssociation.order_id)
            .where(Order.created_at >= since)
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
            .where(Order.created_at >= since)
            .order_by(Order.created_at.desc())
            .limit(8)
        )
    )

    return AdminAnalytics(
        orders_by_status=[
            StatusCount(status=row[0], count=row[1] or 0)
            for row in status_rows
        ],
        orders_over_time=orders_over_time,
        revenue_over_time=series["revenue_over_time"],
        cost_over_time=series["cost_over_time"],
        profit_over_time=series["profit_over_time"],
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
                profit=float(row[3] or 0),
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
        total_orders=len(order_rows),
        total_visitors=int(sum(point.value for point in visitors_over_time)),
        total_page_views=int(sum(point.value for point in page_views_over_time)),
        **profit_metrics,
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


@router.patch(
    "/settings/profit",
    response_model=ProfitSettings,
    status_code=status.HTTP_200_OK,
)
async def update_admin_profit_settings(
    profit_settings: ProfitSettingsUpdate,
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await update_profit_settings(profit_settings)


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
    "/translations/preview",
    response_model=ProductTranslationPreviewResponse,
    status_code=status.HTTP_200_OK,
)
async def preview_admin_product_translations(
    preview_request: ProductTranslationPreviewRequest,
    superuser: Annotated[User, Security(current_active_superuser)],
):
    previews = await preview_product_translations(
        translations=preview_request.translations,
        target_languages=preview_request.target_languages,
    )
    return ProductTranslationPreviewResponse(
        translations=[
            ProductTranslationPreviewItem(
                language_code=preview.language_code,
                product_name=preview.product_name,
                product_description=preview.product_description,
                provider_status=preview.provider_status,
            )
            for preview in previews
        ]
    )


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
