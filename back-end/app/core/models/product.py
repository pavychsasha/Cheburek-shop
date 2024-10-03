from datetime import datetime
import uuid
from sqlalchemy import func, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Product(Base):
    __tablename__ = "Products"

    product_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str]
    price: Mapped[float] = mapped_column(CheckConstraint("price >= 0"), nullable=False)
    category: Mapped[str] = mapped_column(index=True)
    stock_quantity: Mapped[int] = mapped_column(
        CheckConstraint("stock_quantity >= 0"), nullable=False
    )
    image_src: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Optional soft delete field
    deleted_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)

    __table_args__ = (
        Index("ix_product_category", "category"),
        Index("ix_product_price", "price"),
        CheckConstraint("price >= 0", name="check_price_positive"),
        CheckConstraint(
            "stock_quantity >= 0", name="check_stock_quantity_non_negative"
        ),
    )

    def __str__(self) -> str:
        return f"Product<(product_id='{self.product_id!s}', name={self.name!r})>"

    def update_stock(self, quantity: int) -> None:
        """Update stock quantity by adding the given quantity (can be negative)."""
        if self.stock_quantity + quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        self.stock_quantity += quantity
