from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .product import Product


product_tag_association = Table(
    "product_tag_association",
    Base.metadata,
    Column(
        "product_id",
        ForeignKey("Products.product_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("ProductTags.tag_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ProductTag(Base):
    __tablename__ = "ProductTags"

    tag_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    products: Mapped[list["Product"]] = relationship(
        secondary=product_tag_association,
        back_populates="tag_links",
    )
