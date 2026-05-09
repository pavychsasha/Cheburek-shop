from fastapi import HTTPException, status

from app.core.config import settings
from app.core.models import StoreSettings
from app.core.schemas.settings import CurrencySettings, CurrencySettingsUpdate


def _configured_currency_settings() -> CurrencySettings:
    supported_currencies = settings.currency.supported_currency_codes
    rates = settings.currency.rate_mapping
    symbols = settings.currency.symbol_mapping
    for currency in supported_currencies:
        rates.setdefault(currency, 1.0 if currency == settings.currency.base_currency else 0)
        symbols.setdefault(currency, currency)

    return CurrencySettings(
        base_currency=settings.currency.base_currency.upper(),
        default_currency=settings.currency.default_currency.upper(),
        supported_currencies=supported_currencies,
        currency_rates=rates,
        currency_symbols=symbols,
    )


def _settings_to_schema(store_settings: StoreSettings) -> CurrencySettings:
    return CurrencySettings(
        base_currency=store_settings.base_currency,
        default_currency=store_settings.default_currency,
        supported_currencies=store_settings.supported_currencies,
        currency_rates=store_settings.currency_rates,
        currency_symbols=store_settings.currency_symbols,
    )


async def get_store_settings() -> StoreSettings:
    store_settings = await StoreSettings.find_one(
        StoreSettings.settings_key == "default"
    )
    if store_settings is not None:
        return store_settings

    configured = _configured_currency_settings()
    store_settings = StoreSettings(
        settings_key="default",
        base_currency=configured.base_currency,
        default_currency=configured.default_currency,
        supported_currencies=configured.supported_currencies,
        currency_rates=configured.currency_rates,
        currency_symbols=configured.currency_symbols,
    )
    await store_settings.insert()
    return store_settings


async def get_public_currency_settings() -> CurrencySettings:
    return _settings_to_schema(await get_store_settings())


def validate_currency_settings(
    update: CurrencySettingsUpdate,
    *,
    base_currency: str,
) -> None:
    supported = set(update.supported_currencies)
    if base_currency not in supported:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Base currency must be included in supported currencies.",
        )
    if update.default_currency not in supported:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Default currency must be included in supported currencies.",
        )

    missing_rates = sorted(supported.difference(update.currency_rates))
    missing_symbols = sorted(supported.difference(update.currency_symbols))
    if missing_rates or missing_symbols:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Every supported currency must include a rate and symbol. "
                f"Missing rates={missing_rates}, missing symbols={missing_symbols}."
            ),
        )

    invalid_rates = [
        currency
        for currency in supported
        if update.currency_rates.get(currency, 0) <= 0
    ]
    if invalid_rates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Currency rates must be greater than zero: {invalid_rates}.",
        )


async def update_currency_settings(
    update: CurrencySettingsUpdate,
) -> CurrencySettings:
    store_settings = await get_store_settings()
    validate_currency_settings(
        update,
        base_currency=store_settings.base_currency,
    )
    store_settings.default_currency = update.default_currency
    store_settings.supported_currencies = update.supported_currencies
    store_settings.currency_rates = {
        currency: float(update.currency_rates[currency])
        for currency in update.supported_currencies
    }
    store_settings.currency_symbols = {
        currency: str(update.currency_symbols[currency])
        for currency in update.supported_currencies
    }
    await store_settings.save()
    return _settings_to_schema(store_settings)
