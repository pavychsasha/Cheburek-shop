from typing import Optional, List, Annotated
from datetime import datetime
import uuid

from fastapi import Query

from pydantic import BaseModel, Field, ConfigDict


# Country model
class CountryModel(BaseModel):
    country_name: str

    model_config = ConfigDict(from_attributes=True)


# State model with nested Country
class StateModel(BaseModel):
    state_name: str
    country: CountryModel

    model_config = ConfigDict(from_attributes=True)


# City model with nested State
class CityModel(BaseModel):
    city_name: str
    state: StateModel

    model_config = ConfigDict(from_attributes=True)


# OrderAddress model with nested City
class OrderAddress(BaseModel):
    street_name: str
    street_number: str
    apartment_number: str
    zip_code: str
    city: CityModel

    model_config = ConfigDict(from_attributes=True)


# Product translation model
class ProductTranslation(BaseModel):
    product_name: str
    product_description: str
    language_code: str

    model_config = ConfigDict(from_attributes=True)


# Product model with translations
class ProductOrder(BaseModel):
    product_id: uuid.UUID
    stock_quantity: int
    image_src: str
    price: float
    category: str
    translations: List[ProductTranslation]

    model_config = ConfigDict(from_attributes=True)


# OrderProductAssociation model with nested Product
class OrderProductModel(BaseModel):
    product: ProductOrder
    quantity: int

    model_config = ConfigDict(from_attributes=True)


# Main Order model with nested products and address
class OrderModel(BaseModel):
    created_at: datetime
    user_id: Optional[uuid.UUID] = None
    products: List[OrderProductModel]
    total_price: float
    total_count: int
    address: OrderAddress

    model_config = ConfigDict(from_attributes=True)


# Utility function for handling address parameters in API routes
async def order_address_params(
    street_name: Annotated[str, Query(max_length=150)],
    street_number: Annotated[str, Query(max_length=150)],
    apartment_number: Annotated[str, Query(max_length=150)],
    zip_code: Annotated[str, Query(max_length=150)],
    city: Annotated[str, Query(max_length=150)],
    state: Annotated[str, Query(max_length=150)],
    country: Annotated[str, Query(max_length=150)],
):
    return OrderAddress(
        street_name=street_name,
        street_number=street_number,
        apartment_number=apartment_number,
        zip_code=zip_code,
        city=city,
        state=state,
        country=country,
    )
