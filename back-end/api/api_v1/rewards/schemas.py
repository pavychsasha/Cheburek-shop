from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class RewardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    points_required: int = Field(..., ge=0)


class RewardCreate(RewardBase):
    pass


class RewardUpdate(RewardBase):
    pass


class RewardPartialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    points_required: Optional[int] = Field(None, ge=0)

    class ConfigDict:
        from_attributes = True


class RewardInDBBase(RewardBase):
    reward_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class Reward(RewardInDBBase):
    pass
