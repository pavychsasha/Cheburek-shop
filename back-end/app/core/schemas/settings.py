from pydantic import BaseModel, Field, field_validator


class CurrencySettings(BaseModel):
    base_currency: str
    default_currency: str
    supported_currencies: list[str]
    currency_rates: dict[str, float]
    currency_symbols: dict[str, str]


class PublicSettings(BaseModel):
    currency: CurrencySettings


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


class MediaUploadResponse(BaseModel):
    object_name: str
    url: str
    content_type: str
    size: int
