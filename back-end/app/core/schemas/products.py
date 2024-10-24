import re

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List, Annotated
import uuid

from fastapi import Query


# TODO: add it to another folder during refactoring
class Pagination(BaseModel):
    per_page: int
    page: int


class PaginationResponse(BaseModel):
    pages: int


async def pagination_params(
    page: Annotated[int, Query(ge=1, required=False, le=2000)] = 1,
    per_page: Annotated[int, Query(ge=1, required=False)] = 10
):
    return Pagination(per_page=per_page, page=page)


class ProductTranslations(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # translation_id: uuid.UUID = Field(..., exclude=True)
    # product_id: uuid.UUID
    language_code: str
    product_name: str
    product_description: str


class ProductTranslationsPartial(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language_code: str
    product_name: str | None = None
    product_description: str | None = None


class ProductBase(BaseModel):
    translations: list[ProductTranslations]
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

    translations: Optional[list[ProductTranslationsPartial]] = Field(None, min_items=1)
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


class ProductResponse(BaseModel):
    product_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=50)
    stock_quantity: Optional[int] = Field(default=0, ge=0)
    image_src: str = Field(..., min_length=1, max_length=350)


class ProductPaginatedResponse(PaginationResponse):
    products: list[ProductResponse]


class ProductOrder(ProductInDBBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime = Field(..., exclude=True)
    updated_at: datetime = Field(..., exclude=True)
    stock_quantity: Optional[int] = Field(..., exclude=True)
    category: Optional[str] = Field(..., exclude=True)
    image_src: str = Field(..., exclude=True)
