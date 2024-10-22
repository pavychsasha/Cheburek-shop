from typing import TYPE_CHECKING, Annotated

from app.core.models import AccessToken, sql_db_helper
from fastapi import Depends

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_access_tokens_db(
    session: Annotated[
        "AsyncSession",
        Depends(sql_db_helper.session_dependency),
    ]
):
    yield AccessToken.get_db(session=session)
