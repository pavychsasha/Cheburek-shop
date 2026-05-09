export interface CurrencySettings {
    base_currency: string;
    default_currency: string;
    supported_currencies: string[];
    currency_rates: Record<string, number>;
    currency_symbols: Record<string, string>;
}

export interface PublicSettings {
    currency: CurrencySettings;
}
