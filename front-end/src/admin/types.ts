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
    unique_visitors_today: number;
    page_views_today: number;
    total_revenue: number;
    total_recorded_cost: number;
    gross_profit: number;
    estimated_profit: number;
    profit_margin_percent: number;
    average_order_value: number;
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
    cost_price: number;
    category: string;
    stock_quantity: number;
    image_src: string;
    translations?: ProductTranslation[];
    tags?: string[];
}

export interface ProductListResponse {
    pages: number;
    products: AdminProduct[];
}

export interface ProductFormState {
    price: string;
    cost_price: string;
    category: string;
    stock_quantity: string;
    image_src: string;
    tags: string;
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
    profit: number;
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
    cost_over_time: TimeSeriesPoint[];
    profit_over_time: TimeSeriesPoint[];
    visitors_over_time: TimeSeriesPoint[];
    page_views_over_time: TimeSeriesPoint[];
    low_stock_products: LowStockProduct[];
    top_products: TopProduct[];
    recent_orders: RecentOrder[];
    total_revenue: number;
    total_recorded_cost: number;
    gross_profit: number;
    estimated_profit: number;
    profit_margin_percent: number;
    average_order_value: number;
    total_orders: number;
    total_visitors: number;
    total_page_views: number;
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

export interface ProductTranslationPreviewItem extends ProductTranslation {
    provider_status: "translated" | "source" | "draft" | "unavailable";
}

export interface ProductTranslationPreviewResponse {
    translations: ProductTranslationPreviewItem[];
}

export interface AdminOrderProduct {
    product_id?: string | null;
    product_status: string;
    name: string;
    price: number;
    cost_price: number;
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
    customer_notes?: string | null;
    admin_notes?: string | null;
    total_price?: number | null;
    total_count?: number | null;
    products: AdminOrderProduct[];
    address: AdminOrderAddress;
}

export type DashboardChartType = "line" | "bar" | "area" | "pie";

export interface DashboardWidgetPreference {
    id: string;
    visible: boolean;
    chart_type?: DashboardChartType | null;
    position: number;
    timespan_days: number;
    period: "day" | "week" | "month";
}

export interface DashboardPreferences {
    widgets: DashboardWidgetPreference[];
}
