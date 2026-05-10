from typing import Literal
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

OrderStatus = Literal[
    "PENDING",
    "CONFIRMED",
    "PREPARING",
    "READY",
    "DELIVERED",
    "CANCELLED",
]


class AdminSummary(BaseModel):
    products_count: int
    orders_count: int
    users_count: int
    low_stock_products_count: int
    pending_orders_count: int
    unique_visitors_today: int = 0
    page_views_today: int = 0
    total_revenue: float = 0
    total_recorded_cost: float = 0
    gross_profit: float = 0
    estimated_profit: float = 0
    profit_margin_percent: float = 0
    average_order_value: float = 0


class ProductSeedResponse(BaseModel):
    created: int
    updated: int
    skipped: int
    reset: bool
    total_seed_products: int


class StatusCount(BaseModel):
    status: str
    count: int


class TimeSeriesPoint(BaseModel):
    date: date
    value: float


class LowStockProduct(BaseModel):
    product_id: uuid.UUID
    name: str
    stock_quantity: int


class TopProduct(BaseModel):
    name: str
    quantity: int
    revenue: float
    profit: float = 0


class RecentOrder(BaseModel):
    order_id: uuid.UUID
    created_at: datetime
    status: str
    email: str
    total_price: float
    total_count: int


class AdminAnalytics(BaseModel):
    orders_by_status: list[StatusCount]
    orders_over_time: list[TimeSeriesPoint]
    revenue_over_time: list[TimeSeriesPoint]
    cost_over_time: list[TimeSeriesPoint] = Field(default_factory=list)
    profit_over_time: list[TimeSeriesPoint] = Field(default_factory=list)
    visitors_over_time: list[TimeSeriesPoint] = Field(default_factory=list)
    page_views_over_time: list[TimeSeriesPoint] = Field(default_factory=list)
    low_stock_products: list[LowStockProduct]
    top_products: list[TopProduct]
    recent_orders: list[RecentOrder]
    total_revenue: float = 0
    total_recorded_cost: float = 0
    gross_profit: float = 0
    estimated_profit: float = 0
    profit_margin_percent: float = 0
    average_order_value: float = 0
    total_orders: int = 0
    total_visitors: int = 0
    total_page_views: int = 0


class DashboardWidgetPreference(BaseModel):
    id: str
    visible: bool = True
    chart_type: str | None = None
    position: int = 0
    timespan_days: int = Field(default=30, ge=1, le=365)
    period: str = "day"


class DashboardPreferences(BaseModel):
    widgets: list[DashboardWidgetPreference]
