import axios, {AxiosError} from "axios";

import {API_BASE_URL} from "../api/api.ts";
import type {
    AdminOrder,
    AdminAnalytics,
    AdminProduct,
    AdminSummary,
    AdminUser,
    CurrencySettingsUpdate,
    MediaUploadResponse,
    OrderStatus,
    ProductFormState,
    ProductListResponse,
    ProductSeedResponse,
} from "./types.ts";
import type {CurrencySettings, PublicSettings} from "../types/settings.ts";

export const ADMIN_TOKEN_KEY = "cheburek_admin_token";

export const adminApiClient = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
});

adminApiClient.interceptors.request.use((config) => {
    const token = sessionStorage.getItem(ADMIN_TOKEN_KEY);
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

adminApiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response?.status === 401 || error.response?.status === 403) {
            sessionStorage.removeItem(ADMIN_TOKEN_KEY);
        }
        return Promise.reject(error);
    },
);

export const clearAdminToken = () => {
    sessionStorage.removeItem(ADMIN_TOKEN_KEY);
};

export const getAdminErrorMessage = (error: unknown, fallback: string) => {
    if (!axios.isAxiosError(error)) {
        return error instanceof Error ? error.message : fallback;
    }

    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
        return detail;
    }

    if (Array.isArray(detail)) {
        return detail
            .map((item) => item?.msg)
            .filter(Boolean)
            .join(". ");
    }

    return error.message || fallback;
};

export const loginAdmin = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.set("grant_type", "");
    formData.set("username", email);
    formData.set("password", password);
    formData.set("scope", "");
    formData.set("client_id", "");
    formData.set("client_secret", "");

    const tokenResponse = await adminApiClient.post<{access_token: string}>(
        "/auth/login",
        formData,
        {headers: {"Content-Type": "application/x-www-form-urlencoded"}},
    );
    sessionStorage.setItem(ADMIN_TOKEN_KEY, tokenResponse.data.access_token);

    const user = await fetchAdminMe();
    if (!user.is_superuser) {
        clearAdminToken();
        throw new Error("This account does not have admin access.");
    }

    return user;
};

export const fetchAdminMe = async () => {
    const response = await adminApiClient.get<AdminUser>("/users/me");
    return response.data;
};

export const fetchAdminSummary = async () => {
    const response = await adminApiClient.get<AdminSummary>("/admin/summary");
    return response.data;
};

export const fetchAdminAnalytics = async () => {
    const response = await adminApiClient.get<AdminAnalytics>("/admin/analytics");
    return response.data;
};

export const fetchPublicSettings = async () => {
    const response = await adminApiClient.get<PublicSettings>("/settings/public");
    return response.data;
};

export const updateCurrencySettings = async (payload: CurrencySettingsUpdate) => {
    const response = await adminApiClient.patch<CurrencySettings>(
        "/admin/settings/currency",
        payload,
    );
    return response.data;
};

export const uploadProductImage = async (file: File) => {
    const formData = new FormData();
    formData.set("file", file);
    const response = await adminApiClient.post<MediaUploadResponse>(
        "/admin/media/products",
        formData,
        {headers: {"Content-Type": "multipart/form-data"}},
    );
    return response.data;
};

export const fetchProducts = async (query: string) => {
    const response = await adminApiClient.get<ProductListResponse>("/products/search/", {
        params: {
            page: 1,
            per_page: 200,
            name: query || undefined,
        },
    });
    return response.data.products;
};

export const fetchProduct = async (productId: string) => {
    const response = await adminApiClient.get<AdminProduct>(`/products/${productId}/`);
    return response.data;
};

const toProductPayload = (form: ProductFormState) => ({
    price: Number(form.price),
    category: form.category,
    stock_quantity: Number(form.stock_quantity),
    image_src: form.image_src,
    translations: [
        {
            language_code: "en",
            product_name: form.en_name,
            product_description: form.en_description,
        },
        {
            language_code: "ukr",
            product_name: form.ukr_name,
            product_description: form.ukr_description,
        },
    ],
});

export const createProduct = async (form: ProductFormState) => {
    const response = await adminApiClient.post<AdminProduct>("/products/", toProductPayload(form));
    return response.data;
};

export const updateProduct = async (productId: string, form: ProductFormState) => {
    const response = await adminApiClient.put<AdminProduct>(
        `/products/${productId}/`,
        toProductPayload(form),
    );
    return response.data;
};

export const deleteProduct = async (productId: string) => {
    await adminApiClient.delete(`/products/${productId}/`);
};

export const seedProducts = async () => {
    const response = await adminApiClient.post<ProductSeedResponse>("/admin/seed/products");
    return response.data;
};

export const fetchOrders = async () => {
    const response = await adminApiClient.get<AdminOrder[]>("/orders/");
    return response.data;
};

export const updateOrderStatus = async (orderId: string, status: OrderStatus) => {
    await adminApiClient.patch(`/orders/${orderId}/status`, {status});
};

export const deleteOrder = async (orderId: string) => {
    await adminApiClient.delete(`/orders/${orderId}`);
};

export const fetchUsers = async () => {
    const response = await adminApiClient.get<AdminUser[]>("/users/");
    return response.data;
};

export const createUser = async (
    email: string,
    password: string,
    flags: Pick<AdminUser, "is_active" | "is_superuser" | "is_verified">,
) => {
    const response = await adminApiClient.post<AdminUser>("/users/", {
        email,
        password,
        ...flags,
    });
    return response.data;
};

export const updateUserFlags = async (
    userId: string,
    flags: Pick<AdminUser, "is_active" | "is_superuser" | "is_verified">,
) => {
    const response = await adminApiClient.patch<AdminUser>(`/users/${userId}`, flags);
    return response.data;
};

export const deleteUser = async (userId: string) => {
    await adminApiClient.delete(`/users/${userId}`);
};
