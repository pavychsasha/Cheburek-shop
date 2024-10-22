from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base

if TYPE_CHECKING:
    from .product import Product

class ProductTranslation(Base):
    __tablename__ = 'ProductTranslations'
    translation_id = Column(Integer, primary_key=True, autoincrement=True,)
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('Products.product_id', ondelete='CASCADE'),
    )
    product: Mapped[Product] = relationship(back_populates="translations")
    language_code: Mapped[str]
    product_name: Mapped[str]
    product_description: Mapped[str]
