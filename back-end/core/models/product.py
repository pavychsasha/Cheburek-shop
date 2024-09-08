from datetime import datetime
import uuid

from sqlalchemy import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class Product(Base):
    __tablename__ = "Products"

    product_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4(),
    )
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    category: Mapped[str]
    stock_quantity: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )
    image_url: Mapped[str]

    def __str__(self) -> str:
        return f"Product<(product_id='{self.product_id!s}', name={self.name!r})>"
