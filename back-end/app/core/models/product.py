from datetime import datetime
import uuid

# from app.core.models.order_association import OrderProductAssociation
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Product(Base):
    __tablename__ = "Products"

    product_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    price: Mapped[float]
    category: Mapped[str]
    stock_quantity: Mapped[int]
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

    def __str__(self) -> str:
        return f"Product<(product_id='{self.product_id!s}', name={self.name!r})>"
