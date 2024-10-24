from urllib.request import Request

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import LanguageNotFoundError
from app.core.models import ProductTranslation


class LanguagesService:
    @classmethod
    async def get_all_languages(cls, session: AsyncSession):
        stmt = select(
            distinct(ProductTranslation.language_code)
        )
        translations = await session.execute(stmt)
        return translations.scalars().all()

    @classmethod
    async def switch_language(
            cls,
            session: AsyncSession,
            request: Request,
            language: str,
    ):
        all_languages = await LanguagesService.get_all_languages(session=session)

        if language not in all_languages:
            raise LanguageNotFoundError(language)

        if not request.session.get("language"):
            request.session["language"] = language
            return

        request.session["language"] = language
