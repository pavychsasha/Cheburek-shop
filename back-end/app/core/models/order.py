from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import ForeignKey, func, Float, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .product import Product

if TYPE_CHECKING:
    from .user import User
    from .order_association import OrderProductAssociation
    from .address import Address


class Order(Base):
    __tablename__ = "Orders"
    __table_args__ = (UniqueConstraint("address_id", name="uq_order_address_id"),)
    order_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    products: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="order", viewonly=True, cascade="all, delete"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    user: Mapped["User"] = relationship(back_populates="orders")

    address_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Address.address_id"), nullable=False, unique=False
    )
    address: Mapped["Address"] = relationship(
        back_populates="orders", uselist=False, single_parent=True
    )
    email: Mapped[str]
    status: Mapped[str] = mapped_column(default="PENDING")

    total_price: Mapped[float] = mapped_column(Float, default=0)
    total_count: Mapped[int] = mapped_column(Integer, default=0)

    def __str__(self) -> str:
        return f"Order<(order_id='{self.order_id!s}')>"
