from pydantic import BaseModel, Field, field_validator


class CurrencySettings(BaseModel):
    base_currency: str
    default_currency: str
    supported_currencies: list[str]
    currency_rates: dict[str, float]
    currency_symbols: dict[str, str]


class ProductLanguageSettings(BaseModel):
    product_languages: list[str]
    auto_translate_products: bool


class PublicSettings(BaseModel):
    currency: CurrencySettings
    product_languages: ProductLanguageSettings
    category_media: dict[str, str]


class CurrencySettingsUpdate(BaseModel):
    default_currency: str = Field(..., min_length=3, max_length=3)
    supported_currencies: list[str] = Field(..., min_length=1)
    currency_rates: dict[str, float]
    currency_symbols: dict[str, str]

    @field_validator("default_currency")
    @classmethod
    def normalize_default_currency(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("supported_currencies")
    @classmethod
    def normalize_supported_currencies(cls, value: list[str]) -> list[str]:
        normalized = [currency.strip().upper() for currency in value if currency.strip()]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Supported currencies must be unique.")
        return normalized


class ProductLanguageSettingsUpdate(BaseModel):
    product_languages: list[str] = Field(..., min_length=1)
    auto_translate_products: bool = True

    @field_validator("product_languages")
    @classmethod
    def normalize_product_languages(cls, value: list[str]) -> list[str]:
        normalized = [
            language.strip().lower()
            for language in value
            if language.strip()
        ]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Product languages must be unique.")
        return normalized


class ProductTranslationBackfillResponse(BaseModel):
    products_scanned: int
    translations_created: int
    product_languages: list[str]


class MediaUploadResponse(BaseModel):
    object_name: str
    url: str
    content_type: str
    size: int
