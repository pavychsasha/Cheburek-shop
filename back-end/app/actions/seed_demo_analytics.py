from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select

from app.core.models import PageViewDailyStats, VisitorDailyStats, sql_db_helper


DEMO_PATHS = ["/", "/cart", "/order", "/login", "/register", "/admin"]


@dataclass(frozen=True)
class DemoAnalyticsSeedResult:
    visitor_rows: int
    page_rows: int


def demo_visitor_hash(visit_date: date, visitor_index: int) -> str:
    return hashlib.sha256(
        f"demo-visitor:{visit_date.isoformat()}:{visitor_index}".encode("utf-8")
    ).hexdigest()


async def seed_demo_analytics(session=None) -> DemoAnalyticsSeedResult:
    owns_session = session is None
    if owns_session:
        session_context = sql_db_helper.session_factory()
        session = await session_context.__aenter__()
    else:
        session_context = None

    try:
        today = date.today()
        visitor_rows = 0
        page_rows = 0
        for day_index in range(45):
            visit_date = today - timedelta(days=44 - day_index)
            visitors_for_day = 18 + (day_index % 9) * 4 + (day_index // 10)

            for visitor_index in range(visitors_for_day):
                visitor_hash = demo_visitor_hash(visit_date, visitor_index)
                result = await session.execute(
                    select(VisitorDailyStats).where(
                        VisitorDailyStats.visit_date == visit_date,
                        VisitorDailyStats.visitor_hash == visitor_hash,
                    )
                )
                visitor_stat = result.scalar_one_or_none()
                page_views = 1 + (visitor_index % 4)
                if visitor_stat is None:
                    visitor_stat = VisitorDailyStats(
                        visit_date=visit_date,
                        visitor_hash=visitor_hash,
                        page_views=page_views,
                    )
                    session.add(visitor_stat)
                else:
                    visitor_stat.page_views = page_views
                visitor_rows += 1

            for path_index, path in enumerate(DEMO_PATHS):
                result = await session.execute(
                    select(PageViewDailyStats).where(
                        PageViewDailyStats.visit_date == visit_date,
                        PageViewDailyStats.path == path,
                    )
                )
                page_stat = result.scalar_one_or_none()
                views = max(
                    2,
                    int(visitors_for_day * (1.8 if path == "/" else 0.42))
                    + path_index * 3,
                )
                if page_stat is None:
                    page_stat = PageViewDailyStats(
                        visit_date=visit_date,
                        path=path,
                        views=views,
                    )
                    session.add(page_stat)
                else:
                    page_stat.views = views
                page_rows += 1

        await session.commit()
        return DemoAnalyticsSeedResult(
            visitor_rows=visitor_rows,
            page_rows=page_rows,
        )
    except Exception:
        await session.rollback()
        raise
    finally:
        if owns_session and session_context is not None:
            await session_context.__aexit__(None, None, None)


async def main() -> None:
    result = await seed_demo_analytics()
    print(
        "Demo analytics seed complete: "
        f"visitor_rows={result.visitor_rows}, page_rows={result.page_rows}"
    )
    await sql_db_helper.dispose()


if __name__ == "__main__":
    asyncio.run(main())
