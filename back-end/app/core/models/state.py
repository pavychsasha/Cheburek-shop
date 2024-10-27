import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .country import Country
    from .city import City


class State(Base):
    __tablename__ = "State"

    state_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    state_name: Mapped[str] = mapped_column(unique=True, nullable=False)

    cities: Mapped[list["City"]] = relationship(
        back_populates="state",
        cascade="all, delete",
        passive_deletes=True,
    )

    country_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Country.country_id"), nullable=False
    )
    country: Mapped["Country"] = relationship(
        back_populates="states",
        cascade="all, delete",
        passive_deletes=True,
    )
