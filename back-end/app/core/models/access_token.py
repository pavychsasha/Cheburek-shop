from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase, SQLAlchemyBaseAccessTokenTableUUID)
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    @classmethod
    def get_db(cls, session: AsyncSession):
        return SQLAlchemyAccessTokenDatabase(session, cls)
