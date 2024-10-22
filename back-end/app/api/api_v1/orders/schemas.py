from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
import uuid

from app.api.api_v1.products.schemas import ProductOrder


# Pydantic Model for OrderProductAssociation
class OrderProductModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: uuid.UUID = Field(..., exclude=True)
    product_id: uuid.UUID = Field(..., exclude=True)
    order_product_id: uuid.UUID = Field(..., exclude=True)
    product: ProductOrder
    quantity: int


# Pydantic Model for Order
class OrderModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    user_id: Optional[uuid.UUID] = None
    products: List[OrderProductModel]
    total_price: int
    total_count: int

    class ConfigDict:
        orm_mode = True
        from_attributes = True  # This enables compatibility with ORM models
