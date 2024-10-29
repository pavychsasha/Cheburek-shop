from datetime import datetime
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import func, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .order_association import OrderProductAssociation
    from .product_translations import ProductTranslation


class Product(Base):
    __tablename__ = "Products"

    product_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
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

    orders: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="product", cascade="all, delete, delete-orphan"
    )
    translations: Mapped[list["ProductTranslation"]] = relationship()

    __table_args__ = (
        Index("ix_product_category", "category"),
        Index("ix_product_price", "price"),
        CheckConstraint("price >= 0", name="check_price_positive"),
        CheckConstraint(
            "stock_quantity >= 0", name="check_stock_quantity_non_negative"
        ),
    )

    def __str__(self) -> str:
        return f"Product<(product_id='{self.product_id!s}')>"
