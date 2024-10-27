import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

if TYPE_CHECKING:
    from .order import Order
    from .city import City


class Address(Base):
    __tablename__ = "Address"
    __table_args__ = (UniqueConstraint("order_id"),)

    address_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    street_name: Mapped[str]
    street_number: Mapped[str]
    apartment_number: Mapped[str]

    zip_code: Mapped[str]

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("City.city_id")
    )
    city: Mapped["City"] = relationship(
        single_parent=True,
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Orders.order_id"), unique=True
    )
    order: Mapped["Order"] = relationship(
        back_populates="address",
        single_parent=True,
        uselist=False,
        foreign_keys=[order_id],
    )
