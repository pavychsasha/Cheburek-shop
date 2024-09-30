from typing import Annotated, List, Optional
import uuid
from pydantic import Field
from beanie import BackLink, Document, Link


class CartItem(Document):
    product_id: uuid.UUID
    name: str
    price: float = Field(..., ge=0)
    count: int = Field(..., ge=0)
    img_src: str
    total_price: float = Field(..., ge=0)

    class Settings:
        name = "cart_items"


class Cart(Document):
    session_id: uuid.UUID
    items: List[Link[CartItem]] = []
    total_count: int = Field(default=0, ge=0)
    total_price: float = Field(default=0, ge=0)

    class Settings:
        name = "carts"


all_document_models = [CartItem, Cart]
