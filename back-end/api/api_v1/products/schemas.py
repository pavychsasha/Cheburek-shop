import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import uuid


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=50)
    stock_quantity: Optional[int] = Field(default=0, ge=0)
    points: Optional[int] = Field(default=0, ge=0)

    @field_validator("category")
    def no_whitespace(cls, v):
        if v and re.search(r"\s", v):
            raise ValueError(f"{cls.__name__} field must not contain whitespace")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductPartialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    stock_quantity: Optional[int] = Field(None, ge=0)
    points: Optional[int] = Field(None, ge=0)

    @field_validator("category")
    def no_whitespace(cls, v):
        if v and re.search(r"\s", v):
            raise ValueError(f"{cls.__name__} field must not contain whitespace")
        return v

    class ConfigDict:
        orm_mode = True
        from_attributes = True


class ProductInDBBase(ProductBase):
    product_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        orm_mode = True
        from_attributes = True


class Product(ProductInDBBase):
    pass
