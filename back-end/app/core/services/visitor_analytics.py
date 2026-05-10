from __future__ import annotations

import hashlib
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.models.visitor_analytics import PageViewDailyStats, VisitorDailyStats
from app.core.schemas.admin import TimeSeriesPoint


def _hash_visitor_id(visitor_id: str, visit_date: date) -> str:
    raw_value = f"{visit_date.isoformat()}:{visitor_id}:{settings.session.secret_key}"
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()


def normalize_tracking_path(path: str | None) -> str:
    if not path:
        return "/"
    cleaned = path.strip()
    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"
    return cleaned[:250]


async def record_visit(
    session: AsyncSession,
    visitor_id: str,
    path: str | None,
) -> None:
    today = date.today()
    visitor_hash = _hash_visitor_id(visitor_id, today)
    normalized_path = normalize_tracking_path(path)

    visitor_result = await session.execute(
        select(VisitorDailyStats).where(
            VisitorDailyStats.visit_date == today,
            VisitorDailyStats.visitor_hash == visitor_hash,
        )
    )
    visitor_stat = visitor_result.scalar_one_or_none()
    if visitor_stat is None:
        visitor_stat = VisitorDailyStats(
            visit_date=today,
            visitor_hash=visitor_hash,
            page_views=1,
        )
    else:
        visitor_stat.page_views += 1

    page_result = await session.execute(
        select(PageViewDailyStats).where(
            PageViewDailyStats.visit_date == today,
            PageViewDailyStats.path == normalized_path,
        )
    )
    page_stat = page_result.scalar_one_or_none()
    if page_stat is None:
        page_stat = PageViewDailyStats(
            visit_date=today,
            path=normalized_path,
            views=1,
        )
    else:
        page_stat.views += 1

    session.add_all([visitor_stat, page_stat])
    await session.commit()


async def get_today_unique_visitors(session: AsyncSession) -> int:
    return await session.scalar(
        select(func.count())
        .select_from(VisitorDailyStats)
        .where(VisitorDailyStats.visit_date == date.today())
    ) or 0


async def get_today_page_views(session: AsyncSession) -> int:
    return await session.scalar(
        select(func.coalesce(func.sum(PageViewDailyStats.views), 0))
        .where(PageViewDailyStats.visit_date == date.today())
    ) or 0


async def get_visitor_time_series(
    session: AsyncSession,
    *,
    days: int = 14,
) -> tuple[list[TimeSeriesPoint], list[TimeSeriesPoint]]:
    start_date = date.today() - timedelta(days=days - 1)
    visitor_rows = (
        await session.execute(
            select(
                VisitorDailyStats.visit_date,
                func.count(VisitorDailyStats.stat_id),
            )
            .where(VisitorDailyStats.visit_date >= start_date)
            .group_by(VisitorDailyStats.visit_date)
            .order_by(VisitorDailyStats.visit_date)
        )
    ).all()
    page_view_rows = (
        await session.execute(
            select(
                PageViewDailyStats.visit_date,
                func.coalesce(func.sum(PageViewDailyStats.views), 0),
            )
            .where(PageViewDailyStats.visit_date >= start_date)
            .group_by(PageViewDailyStats.visit_date)
            .order_by(PageViewDailyStats.visit_date)
        )
    ).all()

    return (
        [
            TimeSeriesPoint(date=row[0], value=float(row[1] or 0))
            for row in visitor_rows
        ],
        [
            TimeSeriesPoint(date=row[0], value=float(row[1] or 0))
            for row in page_view_rows
        ],
    )
