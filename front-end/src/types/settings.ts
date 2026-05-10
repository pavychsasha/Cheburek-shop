export interface CurrencySettings {
    base_currency: string;
    default_currency: string;
    supported_currencies: string[];
    currency_rates: Record<string, number>;
    currency_symbols: Record<string, string>;
}

export interface ProductLanguageSettings {
    product_languages: string[];
    auto_translate_products: boolean;
}

export interface PublicSettings {
    currency: CurrencySettings;
    product_languages: ProductLanguageSettings;
}
