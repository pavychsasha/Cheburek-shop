from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped["str"]

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, User)

    def __str__(self) -> str:
        return f"User<(user_id='{self.id!s}')>"
