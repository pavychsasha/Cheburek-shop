from typing import List, Optional
import uuid
from pydantic import ConfigDict, Field
from beanie import Document, Link


class CartItem(Document):
    model_config = ConfigDict(populate_by_name=True)

    product_id: uuid.UUID
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0, alias="count")
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
