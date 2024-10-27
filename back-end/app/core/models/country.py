import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .state import State


class Country(Base):
    __tablename__ = "Country"

    country_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    country_name: Mapped[str] = mapped_column(unique=True, nullable=False)

    states: Mapped[list["State"]] = relationship(
        back_populates="country",
        cascade="all, delete",
        passive_deletes=True,
    )
