from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from .order import Order


class User(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped["str"]
    orders: Mapped[list[Order]] = relationship(back_populates="user")

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, User)

    def __str__(self) -> str:
        return f"User<(user_id='{self.id!s}, username={self.username!r}')>"
