from typing import Annotated

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.session import current_language
from app.core.models import sql_db_helper
from .services import LanguagesService

router = APIRouter(
    tags=["Languages"],
)


@router.get("/")
async def get_languages(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)]
):
    """
    Get all languages
    """
    return await LanguagesService.get_all_languages(session=session)


@router.get("/current_language")
async def get_current_language(current_language: Annotated[str, Depends(current_language)]):
    return {"language": current_language}


@router.post("/change_language")
async def switch_language(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    request: Request,
    language: Annotated[str | None, Query(min_length=1, max_length=5)] = None
):

    return await LanguagesService.switch_language(
        language=language,
        session=session,
        request=request,
    )
