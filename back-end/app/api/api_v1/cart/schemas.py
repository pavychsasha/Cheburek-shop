from typing import Optional, List
import uuid
from pydantic import BaseModel, Field


class CartItemModel(BaseModel):
    product_id: uuid.UUID
    name: str
    price: float
    count: int
    img_src: str
    total_price: float


class CartItemModify(BaseModel):
    product_id: uuid.UUID
    count: int


class CartModel(BaseModel):
    items: List[Optional[CartItemModel]] = []
    total_count: int = 0
    total_price: float = 0
