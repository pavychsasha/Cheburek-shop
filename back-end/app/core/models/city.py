import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .address import Address
    from .state import State


class City(Base):
    __tablename__ = "City"
    __table_args__ = (
        UniqueConstraint("city_name", "state_id", name="uq_city_name_state_id"),
    )
    city_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    city_name: Mapped[str]
    # country_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("Country.country_id"))
    state_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("State.state_id"), nullable=False
    )
    state: Mapped["State"] = relationship(back_populates="cities")

    addresses: Mapped[list["Address"]] = relationship(
        back_populates="city",
        cascade="all, delete",
        passive_deletes=True,
    )
