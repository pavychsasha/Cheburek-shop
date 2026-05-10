from typing import Literal, Optional, List, Annotated
from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationError

from fastapi import Query, HTTPException

OrderStatus = Literal[
    "PENDING",
    "CONFIRMED",
    "PREPARING",
    "READY",
    "DELIVERED",
    "CANCELLED",
]


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


class OrderAddressInfo(BaseModel):
    street_name: str
    street_number: str
    apartment_number: str
    zip_code: str
    city: str
    state: str
    country: str


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
    product: Optional[ProductOrder] = None  # in case order has been deleted
    quantity: int

    model_config = ConfigDict(from_attributes=True)


# Main Order model with nested products and address
class OrderModel(BaseModel):
    created_at: datetime
    user_id: Optional[uuid.UUID] = None
    status: str
    email: EmailStr
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    products: List[OrderProductModel]

    # TODO: SAVE PRODUCTS NAME, ORDERS TOTAL PRICE AND COUNT IN CASE PRODUCT HAS BEEN DELETED
    total_price: Optional[float] = None
    total_count: Optional[int] = None
    address: OrderAddressInfo


class OrderProductResponseModel(BaseModel):
    product_id: Optional[uuid.UUID] = None  # in case a product has been deleted
    product_status: str
    name: str
    price: float
    category: str
    image_src: str
    quantity: int


class OrderResponseModel(BaseModel):
    order_id: uuid.UUID
    created_at: datetime
    user_id: Optional[uuid.UUID] = None
    status: OrderStatus | str
    email: EmailStr
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    # TODO: SAVE PRODUCTS NAME, ORDERS TOTAL PRICE AND COUNT IN CASE PRODUCT HAS BEEN DELETED
    total_price: Optional[float] = None
    total_count: Optional[int] = None
    products: List[OrderProductResponseModel]

    address: OrderAddressInfo


class OrderResponse(BaseModel):
    orders: List[OrderResponseModel] = Field(default_factory=list)


class ContactData(BaseModel):
    email: EmailStr
    customer_notes: Optional[str] = Field(None, max_length=500)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderStatusResponse(BaseModel):
    order_id: uuid.UUID
    status: OrderStatus


class OrderNotesUpdate(BaseModel):
    admin_notes: Optional[str] = Field(None, max_length=1000)


class OrderNotesResponse(BaseModel):
    order_id: uuid.UUID
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None


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
    return OrderAddressInfo(
        street_name=street_name,
        street_number=street_number,
        apartment_number=apartment_number,
        zip_code=zip_code,
        city=city,
        state=state,
        country=country,
    )


async def contact_data_params(
    email: Annotated[str, Query(max_length=150)],
    customer_notes: Annotated[str | None, Query(max_length=500)] = None,
) -> ContactData:
    # Validate the email within the ContactData model
    try:
        return ContactData(email=email, customer_notes=customer_notes)
    except ValidationError as e:
        # Raise a 422 HTTPException with details if validation fails
        raise HTTPException(status_code=422, detail=e.errors())
