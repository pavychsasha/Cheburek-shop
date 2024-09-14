from typing import List, Optional, Any
import uuid
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)  # Convert ObjectId to a string


# CartItem model representing each item in the cart
class CartItem(BaseModel):
    product_id: uuid.UUID = Field(...)
    quantity: int = Field(..., gt=0)


# Cart model for creating/retrieving full cart details
class Cart(BaseModel):
    id: PyObjectId = Field(
        default_factory=PyObjectId, alias="_id"
    )  # Automatically convert _id to string

    user_id: Optional[uuid.UUID] = Field(None)
    session_id: Optional[uuid.UUID]
    items: List[CartItem] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": None,
                "items": [{"product_id": "12345", "quantity": 2}],
                "_id": "66e5132d122b3ec83fa91ab6",
            }
        }
        json_encoders = {ObjectId: str}


# CartItemCount model for returning just the count of items in the cart
class CartItemCount(BaseModel):
    total_items: int

    class Config:
        json_schema_extra = {"example": {"total_items": 5}}


# CartUpdate model for updating cart items
class CartUpdate(BaseModel):
    items: Optional[List[CartItem]] = None
