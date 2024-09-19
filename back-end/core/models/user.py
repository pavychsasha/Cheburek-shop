from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import (
    DateTime,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase

if TYPE_CHECKING:
    # from core.models.order import Order
    from sqlalchemy.ext.asyncio import AsyncSession


# class User(Base):
#     __tablename__ = "Users"

#     user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
#     username: Mapped[str] = mapped_column(unique=True, nullable=False)
#     email: Mapped[str] = mapped_column(unique=True, nullable=False)
#     password: Mapped[str] = mapped_column(nullable=False)
#     reward_points: Mapped[int] = mapped_column(
#         default=0,
#         server_default="0",
#     )
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=func.now(),
#         server_default=func.now(),
#     )
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=func.now(),
#         server_default=func.now(),
#     )

#     orders: Mapped[list[Order]] = relationship(back_populates="user")

#     def __str__(self) -> str:
#         return f"User<(user_id='{self.user_id!s}', username={self.username!r})>"


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, User)
