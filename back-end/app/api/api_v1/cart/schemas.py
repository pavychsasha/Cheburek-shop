from typing import Optional, List
import uuid
from pydantic import BaseModel, Field


class CartItemModel(BaseModel):
    product_id: uuid.UUID
    price: float = Field(..., gt=0)
    count: int = Field(..., gt=0)
    total_price: float = Field(..., gt=0)

class CartItemResponse(CartItemModel):
    name: str
    image_src: str

class CartModelResponse(BaseModel):
    items: List[Optional[CartItemResponse]] = []
    total_count: int = 0
    total_price: float = 0

class CartItemModify(BaseModel):
    product_id: uuid.UUID
    count: int = Field(..., gt=0)


class CartModel(BaseModel):
    items: List[Optional[CartItemModel]] = []
    total_count: int = 0
    total_price: float = 0

    class ConfigDict:
        orm_mode = True
        from_attributes = True


class CartOrder(BaseModel):
    items: list[CartItemModel] = Field(..., min_length=1)
    total_count: int = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
