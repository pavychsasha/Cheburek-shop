import type {CurrencySettings} from "../types/settings.ts";

export const fallbackCurrencySettings: CurrencySettings = {
    base_currency: "UAH",
    default_currency: "UAH",
    supported_currencies: ["UAH", "USD", "EUR"],
    currency_rates: {
        UAH: 1,
        USD: 0.024,
        EUR: 0.022,
    },
    currency_symbols: {
        UAH: "₴",
        USD: "$",
        EUR: "€",
    },
};

export const convertFromBaseCurrency = (
    amount: number,
    settings: CurrencySettings,
    displayCurrency: string,
) => {
    const rate = settings.currency_rates[displayCurrency] ?? 1;
    return amount * rate;
};

export const formatCurrency = (
    amount: number,
    settings: CurrencySettings,
    displayCurrency: string,
) => {
    const normalizedCurrency = settings.supported_currencies.includes(displayCurrency)
        ? displayCurrency
        : settings.default_currency;
    const convertedAmount = convertFromBaseCurrency(amount, settings, normalizedCurrency);

    try {
        return new Intl.NumberFormat("uk-UA", {
            style: "currency",
            currency: normalizedCurrency,
            maximumFractionDigits: normalizedCurrency === settings.base_currency ? 0 : 2,
        }).format(convertedAmount);
    } catch {
        const symbol = settings.currency_symbols[normalizedCurrency] ?? normalizedCurrency;
        return `${convertedAmount.toFixed(2)} ${symbol}`;
    }
};
