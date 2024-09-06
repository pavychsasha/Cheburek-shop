from datetime import datetime
import uuid
from core.models.base import Base

from core.models.order_association import OrderRewardAssociation
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Reward(Base):
    __tablename__ = "Rewards"

    reward_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    name: Mapped[str]
    description: Mapped[str]
    points_required: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )

    orders: Mapped[list[OrderRewardAssociation]] = relationship(back_populates="reward")

    def __str__(self) -> str:
        return f"Reward<(reward_id='{self.reward_id!s}', name={self.name!r})>"
