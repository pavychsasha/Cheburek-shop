from typing import Literal

from pydantic import BaseModel

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


class ProductSeedResponse(BaseModel):
    created: int
    updated: int
    skipped: int
    reset: bool
    total_seed_products: int
