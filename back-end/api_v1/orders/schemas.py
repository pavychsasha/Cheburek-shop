from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:

    from core.models import OrderProductAssociation, OrderRewardAssociation


class OrderBase(BaseModel):
    user_id: uuid.UUID
    status: str = Field(default="pending", max_length=50)
    payment_method: str = Field(default="card", max_length=50)
    stripe_payment_id: str | None = None
    # products_data: dict[uuid.UUID, float]


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    pass


class OrderPartialUpdate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    order_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)
    payment_method: Optional[str] = Field(None, max_length=50)
    stripe_payment_id: str | None = None
    product_ids: list[uuid.UUID] = None

    class ConfigDict:
        from_attributes = True


class OrderInDBBase(OrderBase):
    order_id: uuid.UUID

    class ConfigDict:
        from_attributes = True


class Order(OrderInDBBase):
    products: list[OrderProductAssociation] = []
    rewards: list[OrderRewardAssociation] = []


class OrderProductAssociationBase(BaseModel):
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)


class OrderProductAssociationCreate(OrderProductAssociationBase):
    pass


class OrderProductAssociationUpdate(OrderProductAssociationBase):
    pass


class OrderProductAssociationInDBBase(OrderProductAssociationBase):
    order_product_id: uuid.UUID

    class ConfigDict:
        from_attributes = True


class OrderRewardAssociationBase(BaseModel):
    order_id: uuid.UUID
    reward_id: uuid.UUID
    points_redeemed: int = Field(..., ge=0)


class OrderRewardAssociationPartialUpdate(BaseModel):
    order_id: Optional[uuid.UUID] = None
    reward_id: Optional[uuid.UUID] = None
    points_redeemed: Optional[int] = Field(None, ge=0)

    class ConfigDict:
        from_attributes = True


class OrderRewardAssociationCreate(OrderRewardAssociationBase):
    pass


class OrderRewardAssociationUpdate(OrderRewardAssociationBase):
    pass


class OrderRewardAssociationInDBBase(OrderRewardAssociationBase):
    order_reward_id: uuid.UUID

    class ConfigDict:
        from_attributes = True
