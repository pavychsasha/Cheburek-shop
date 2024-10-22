from typing import TYPE_CHECKING, Annotated

from app.core.models import User, sql_db_helper
from fastapi import Depends

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_users_db(
    session: Annotated[
        "AsyncSession",
        Depends(sql_db_helper.session_dependency),
    ]
):
    yield User.get_db(session=session)
