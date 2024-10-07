import re
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
import uuid


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=50)
    stock_quantity: Optional[int] = Field(default=0, ge=0)
    image_src: str = Field(..., min_length=1, max_length=350)

    @field_validator("category")
    def no_whitespace(cls, v):
        if v and re.search(r"\s", v):
            raise ValueError(f"{cls.__name__} field must not contain whitespace")
        return v


class ProductCreate(ProductBase):
    pass


class ProductBulkCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    products: List[ProductCreate]


class ProductUpdate(ProductBase):
    pass


class ProductPartialUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    stock_quantity: Optional[int] = Field(None, ge=0)
    points: Optional[int] = Field(None, ge=0)
    image_src: Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    def no_whitespace(cls, v):
        if v and re.search(r"\s", v):
            raise ValueError(f"{cls.__name__} field must not contain whitespace")
        return v


class ProductInDBBase(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class Product(ProductInDBBase):
    pass


class ProductOrder(ProductInDBBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime = Field(..., exclude=True)
    updated_at: datetime = Field(..., exclude=True)
    stock_quantity: Optional[int] = Field(..., exclude=True)
    category: Optional[str] = Field(..., exclude=True)
    image_src: str = Field(..., exclude=True)
    description: str = Field(..., exclude=True)
