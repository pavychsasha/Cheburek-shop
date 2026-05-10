import type {CurrencySettings, ProductLanguageSettings} from "../types/settings.ts";

export type AdminView = "dashboard" | "products" | "orders" | "users" | "settings";

export type OrderStatus =
    | "PENDING"
    | "CONFIRMED"
    | "PREPARING"
    | "READY"
    | "DELIVERED"
    | "CANCELLED";

export interface AdminUser {
    id: string;
    email: string;
    is_active: boolean;
    is_superuser: boolean;
    is_verified: boolean;
}

export interface AdminSummary {
    products_count: number;
    orders_count: number;
    users_count: number;
    low_stock_products_count: number;
    pending_orders_count: number;
}

export interface ProductTranslation {
    language_code: string;
    product_name: string;
    product_description: string;
}

export interface AdminProduct {
    product_id: string;
    name?: string;
    description?: string;
    price: number;
    category: string;
    stock_quantity: number;
    image_src: string;
    translations?: ProductTranslation[];
}

export interface ProductListResponse {
    pages: number;
    products: AdminProduct[];
}

export interface ProductFormState {
    price: string;
    category: string;
    stock_quantity: string;
    image_src: string;
    translations: ProductTranslation[];
}

export interface ProductSeedResponse {
    created: number;
    updated: number;
    skipped: number;
    reset: boolean;
    total_seed_products: number;
}

export interface StatusCount {
    status: string;
    count: number;
}

export interface TimeSeriesPoint {
    date: string;
    value: number;
}

export interface LowStockProduct {
    product_id: string;
    name: string;
    stock_quantity: number;
}

export interface TopProduct {
    name: string;
    quantity: number;
    revenue: number;
}

export interface RecentOrder {
    order_id: string;
    created_at: string;
    status: string;
    email: string;
    total_price: number;
    total_count: number;
}

export interface AdminAnalytics {
    orders_by_status: StatusCount[];
    orders_over_time: TimeSeriesPoint[];
    revenue_over_time: TimeSeriesPoint[];
    low_stock_products: LowStockProduct[];
    top_products: TopProduct[];
    recent_orders: RecentOrder[];
}

export interface MediaUploadResponse {
    object_name: string;
    url: string;
    content_type: string;
    size: number;
}

export type CurrencySettingsUpdate = Pick<
    CurrencySettings,
    "default_currency" | "supported_currencies" | "currency_rates" | "currency_symbols"
>;

export type ProductLanguageSettingsUpdate = ProductLanguageSettings;

export interface ProductTranslationBackfillResponse {
    products_scanned: number;
    translations_created: number;
    product_languages: string[];
}

export interface AdminOrderProduct {
    product_id?: string | null;
    product_status: string;
    name: string;
    price: number;
    category: string;
    image_src: string;
    quantity: number;
}

export interface AdminOrderAddress {
    street_name: string;
    street_number: string;
    apartment_number: string;
    zip_code: string;
    city: string;
    state: string;
    country: string;
}

export interface AdminOrder {
    order_id: string;
    created_at: string;
    user_id?: string | null;
    status: OrderStatus;
    email: string;
    total_price?: number | null;
    total_count?: number | null;
    products: AdminOrderProduct[];
    address: AdminOrderAddress;
}
