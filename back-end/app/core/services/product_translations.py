from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.models import Product, ProductTranslation, redis_db_helper
from app.core.config import settings as app_settings
from app.core.schemas.products import ProductTranslations
from app.core.schemas.settings import (
    ProductLanguageSettings,
    ProductTranslationBackfillResponse,
)
from app.core.services.store_settings import get_product_language_settings
from app.core.services.translation import (
    TranslationPreviewItem,
    translate_product_fields,
)


def _draft_translation_name(source_name: str, language_code: str) -> str:
    if language_code == "en":
        return source_name

    suffix = f" ({language_code.upper()})"
    if source_name.endswith(suffix):
        return source_name
    return f"{source_name}{suffix}"


def _source_translation(
    translations: list[ProductTranslations],
) -> ProductTranslations | None:
    english_translation = next(
        (
            translation
            for translation in translations
            if translation.language_code == "en"
        ),
        None,
    )
    return english_translation or (translations[0] if translations else None)


def _normalize_translations(
    translations: list[ProductTranslations],
) -> list[ProductTranslations]:
    normalized: dict[str, ProductTranslations] = {}
    for translation in translations:
        language_code = translation.language_code.strip().lower()
        if not language_code:
            continue
        normalized[language_code] = ProductTranslations(
            language_code=language_code,
            product_name=translation.product_name.strip(),
            product_description=translation.product_description.strip(),
        )
    return list(normalized.values())


async def _get_product_language_settings_safe() -> ProductLanguageSettings:
    try:
        return await get_product_language_settings()
    except Exception:
        return ProductLanguageSettings(
            product_languages=app_settings.product_languages.language_codes,
            auto_translate_products=(
                app_settings.product_languages.auto_translate_products
            ),
        )


async def complete_product_translations(
    translations: list[ProductTranslations],
) -> list[ProductTranslations]:
    normalized = _normalize_translations(translations)
    if not normalized:
        return normalized

    settings = await _get_product_language_settings_safe()
    if not settings.auto_translate_products:
        return normalized

    source = _source_translation(normalized)
    if source is None:
        return normalized

    translations_by_language = {
        translation.language_code: translation
        for translation in normalized
    }
    for language_code in settings.product_languages:
        if language_code not in translations_by_language:
            translated = await translate_product_fields(source, language_code)
            if translated.provider_status == "unavailable":
                continue
            normalized.append(
                ProductTranslations(
                    language_code=language_code,
                    product_name=translated.product_name,
                    product_description=translated.product_description,
                )
            )

    return normalized


async def backfill_product_translations(
    session: AsyncSession,
) -> ProductTranslationBackfillResponse:
    settings = await _get_product_language_settings_safe()
    stmt = select(Product).options(joinedload(Product.translations))
    result = await session.execute(stmt)
    products = result.unique().scalars().all()
    created = 0

    for product in products:
        translations_by_language = {
            translation.language_code: translation
            for translation in product.translations
        }
        source = translations_by_language.get("en") or next(
            iter(translations_by_language.values()),
            None,
        )
        if source is None:
            continue

        for language_code in settings.product_languages:
            if language_code in translations_by_language:
                continue
            translated = await translate_product_fields(source, language_code)
            if translated.provider_status == "unavailable":
                continue
            product.translations.append(
                ProductTranslation(
                    language_code=language_code,
                    product_name=translated.product_name,
                    product_description=translated.product_description,
                )
            )
            created += 1

    await session.commit()
    if redis_db_helper.cache is not None:
        await redis_db_helper.cache.remove_all_cache_keys()

    return ProductTranslationBackfillResponse(
        products_scanned=len(products),
        translations_created=created,
        product_languages=settings.product_languages,
    )


async def preview_product_translations(
    translations: list[ProductTranslations],
    target_languages: list[str],
) -> list[TranslationPreviewItem]:
    normalized = _normalize_translations(translations)
    source = _source_translation(normalized)
    if source is None:
        return []

    source_language = source.language_code
    previews: list[TranslationPreviewItem] = []
    for language_code in target_languages:
        normalized_language = language_code.strip().lower()
        if not normalized_language or normalized_language == source_language:
            continue
        previews.append(await translate_product_fields(source, normalized_language))
    return previews
