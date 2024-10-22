import uuid
from typing import List, Optional

from beanie import Document, Link
from pydantic import Field


class CartItem(Document):
    product_id: uuid.UUID
    price: float = Field(..., ge=0)
    count: int = Field(..., ge=0)
    total_price: float = Field(..., ge=0)

    class Settings:
        name = "cart_items"


class Cart(Document):
    session_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    items: List[Link[CartItem]] = []
    total_count: int = Field(default=0, ge=0)
    total_price: float = Field(default=0, ge=0)

    class Settings:
        name = "carts"


all_document_models = [CartItem, Cart]
