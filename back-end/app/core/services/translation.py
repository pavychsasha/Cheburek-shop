from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from urllib import error, request

from app.core.config import settings
from app.core.schemas.products import ProductTranslations


LANGUAGE_ALIASES = {
    "ukr": "uk",
    "ua": "uk",
    "eng": "en",
}


@dataclass(frozen=True)
class TranslationPreviewItem:
    language_code: str
    product_name: str
    product_description: str
    provider_status: str


def provider_language_code(language_code: str) -> str:
    normalized = language_code.strip().lower()
    return LANGUAGE_ALIASES.get(normalized, normalized)


def draft_translation(
    language_code: str,
    source: ProductTranslations,
) -> TranslationPreviewItem:
    suffix = f" ({language_code.upper()})"
    name = source.product_name
    if language_code != settings.translation.source_language and not name.endswith(suffix):
        name = f"{name}{suffix}"
    return TranslationPreviewItem(
        language_code=language_code,
        product_name=name,
        product_description=source.product_description,
        provider_status="draft",
    )


def _translate_text_sync(text: str, target_language: str) -> str:
    payload = json.dumps(
        {
            "q": text,
            "source": provider_language_code(settings.translation.source_language),
            "target": provider_language_code(target_language),
            "format": "text",
        }
    ).encode("utf-8")
    translate_url = settings.translation.base_url.rstrip("/") + "/translate"
    req = request.Request(
        translate_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=settings.translation.timeout_seconds) as response:
        body = json.loads(response.read().decode("utf-8"))

    translated_text = body.get("translatedText")
    if not isinstance(translated_text, str) or not translated_text.strip():
        raise ValueError("Translation response did not include translated text.")
    return translated_text.strip()


async def translate_text(text: str, target_language: str) -> str:
    return await asyncio.to_thread(_translate_text_sync, text, target_language)


def _check_translation_service_sync() -> None:
    health_url = settings.translation.base_url.rstrip("/") + "/languages"
    req = request.Request(health_url, method="GET")
    with request.urlopen(req, timeout=settings.translation.timeout_seconds) as response:
        if response.status >= 400:
            raise RuntimeError(f"Translation service returned {response.status}")


async def check_translation_service() -> None:
    if not settings.translation.enabled:
        return
    await asyncio.to_thread(_check_translation_service_sync)


async def translate_product_fields(
    source: ProductTranslations,
    target_language: str,
) -> TranslationPreviewItem:
    normalized_target = target_language.strip().lower()
    if not normalized_target:
        return draft_translation(target_language, source)

    if provider_language_code(normalized_target) == provider_language_code(
        settings.translation.source_language
    ):
        return TranslationPreviewItem(
            language_code=normalized_target,
            product_name=source.product_name,
            product_description=source.product_description,
            provider_status="source",
        )

    if not settings.translation.enabled:
        return draft_translation(normalized_target, source)

    try:
        translated_name, translated_description = await asyncio.gather(
            translate_text(source.product_name, normalized_target),
            translate_text(source.product_description, normalized_target),
        )
    except (TimeoutError, ValueError, error.URLError, error.HTTPError, OSError):
        return TranslationPreviewItem(
            language_code=normalized_target,
            product_name=source.product_name,
            product_description=source.product_description,
            provider_status="unavailable",
        )

    provider_status = "translated"
    if translated_name.casefold() == source.product_name.casefold():
        translated_name = draft_translation(normalized_target, source).product_name
        provider_status = "draft"

    return TranslationPreviewItem(
        language_code=normalized_target,
        product_name=translated_name,
        product_description=translated_description,
        provider_status=provider_status,
    )
