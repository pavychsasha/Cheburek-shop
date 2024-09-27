from typing import Optional, List
import uuid
from pydantic import BaseModel, Field


class CartItemModel(BaseModel):
    product_id: uuid.UUID
    count: int
