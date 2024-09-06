from datetime import datetime
import uuid

from core.models.order_association import (
    OrderProductAssociation,
    OrderRewardAssociation,
)
from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.user import User


class Order(Base):
    __tablename__ = "Orders"

    order_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Users.user_id"))
    order_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    status: Mapped[str] = mapped_column(String(50), default="pending")
    payment_method: Mapped[str] = mapped_column(default="card")
    stripe_payment_id: Mapped[str | None]  # TODO: later it would be nullable=false

    user: Mapped[User] = relationship(back_populates="orders")

    products: Mapped[list[OrderProductAssociation]] = relationship(
        back_populates="order"
    )
    rewards: Mapped[list[OrderRewardAssociation]] = relationship(back_populates="order")

    def __str__(self) -> str:
        return f"Order<(order_id='{self.order_id!r}')>"

    @property
    def total_price(self):
        if not hasattr(self, "_total_price"):
            self._total_price = 0
            for association in self.products:
                self._total_price += association.product.price * association.quantity
        return self._total_price

    @total_price.setter
    def total_price(self, new_price):
        self._total_price = new_price
