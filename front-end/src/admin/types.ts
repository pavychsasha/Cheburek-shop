export type AdminView = "dashboard" | "products" | "orders" | "users";

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
    en_name: string;
    en_description: string;
    ukr_name: string;
    ukr_description: string;
}

export interface ProductSeedResponse {
    created: number;
    updated: number;
    skipped: number;
    reset: boolean;
    total_seed_products: number;
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
