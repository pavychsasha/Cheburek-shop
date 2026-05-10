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

export interface ProfitSettings {
    fallback_profit_margin: number;
}

export interface TranslationServiceStatus {
    enabled: boolean;
    status: string;
}

export interface PublicSettings {
    currency: CurrencySettings;
    product_languages: ProductLanguageSettings;
    category_media: Record<string, string>;
    profit: ProfitSettings;
    translation: TranslationServiceStatus;
}
