from typing import TYPE_CHECKING, Annotated

from core.models import db_helper
from core.models import User
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_users_db(
    session: Annotated[
        "AsyncSession",
        Depends(db_helper.session_dependency),
    ]
):
    yield User.get_db(session=session)
