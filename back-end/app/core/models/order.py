from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base
from .product import Product

if TYPE_CHECKING:
    from .user import User
    from .order_association import OrderProductAssociation


class Order(Base):
    __tablename__ = "Orders"

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

    def __str__(self) -> str:
        return f"Order<(order_id='{self.order_id!s}')>"

    @hybrid_property
    def total_price(self):
        return sum(
            product.product.price * product.quantity for product in self.products
        )

    @total_price.expression
    def total_price(cls):
        return (
            select(func.sum(OrderProductAssociation.quantity * Product.price))
            .join(Product)
            .where(OrderProductAssociation.order_id == cls.order_id)
            .correlate(cls)
            .label("total_price")
        )

    @hybrid_property
    def total_count(self):
        return sum(product.quantity for product in self.products)

    @total_count.expression
    def total_count(cls):
        return (
            select(func.sum(OrderProductAssociation.quantity))
            .where(OrderProductAssociation.order_id == cls.order_id)
            .correlate(cls)
            .label("total_count")
        )
