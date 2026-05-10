import uuid
from datetime import date

from sqlalchemy import Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class VisitorDailyStats(Base):
    __tablename__ = "VisitorDailyStats"
    __table_args__ = (
        UniqueConstraint(
            "visit_date",
            "visitor_hash",
            name="uq_visitor_daily_hash",
        ),
    )

    stat_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    visit_date: Mapped[date] = mapped_column(Date, index=True)
    visitor_hash: Mapped[str] = mapped_column(String(64))
    page_views: Mapped[int] = mapped_column(Integer, default=1, server_default="1")


class PageViewDailyStats(Base):
    __tablename__ = "PageViewDailyStats"
    __table_args__ = (
        UniqueConstraint(
            "visit_date",
            "path",
            name="uq_page_view_daily_path",
        ),
    )

    stat_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    visit_date: Mapped[date] = mapped_column(Date, index=True)
    path: Mapped[str] = mapped_column(String(250))
    views: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
