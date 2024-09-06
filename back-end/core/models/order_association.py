from __future__ import annotations
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .order import Order
    from .product import Product
    from .rewards import Reward


class OrderProductAssociation(Base):
    __tablename__ = "order_product_association"
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "product_id",
            name="idx_unique_order_product",
        ),
    )

    order_product_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Orders.order_id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Products.product_id"))

    quantity: Mapped[int] = mapped_column(default=1, server_default="1")

    # association between Assocation -> Order
    order: Mapped[Order] = relationship(
        back_populates="products",
    )
    # association between Assocation -> Product
    product: Mapped[Product] = relationship(
        back_populates="orders",
    )


class OrderRewardAssociation(Base):
    __tablename__ = "order_reward_association"
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "reward_id",
            name="idx_unique_order_reward",
        ),
    )

    order_reward_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Orders.order_id"))
    reward_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Rewards.reward_id"))
    points_redeemed: Mapped[int]

    # association between Assocation -> Order
    order: Mapped[Order] = relationship(
        back_populates="rewards",
    )
    # association between Assocation -> Product
    reward: Mapped[Reward] = relationship(
        back_populates="orders",
    )
