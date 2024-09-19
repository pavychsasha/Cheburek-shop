from typing import TYPE_CHECKING, Annotated

from core.models import AccessToken
from core.models import db_helper
from fastapi import Depends


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_access_tokens_db(
    session: Annotated[
        "AsyncSession",
        Depends(db_helper.session_dependency),
    ]
):
    yield AccessToken.get_db(session=session)
