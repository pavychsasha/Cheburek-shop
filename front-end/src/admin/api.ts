import axios, {AxiosError} from "axios";

import {API_BASE_URL} from "../api/api.ts";
import type {
    AdminOrder,
    AdminAnalytics,
    AdminProduct,
    AdminSummary,
    AdminUser,
    CurrencySettingsUpdate,
    DashboardPreferences,
    MediaUploadResponse,
    OrderStatus,
    ProductLanguageSettingsUpdate,
    ProductFormState,
    ProductListResponse,
    ProductSeedResponse,
    ProductTranslationBackfillResponse,
} from "./types.ts";
import type {CurrencySettings, ProductLanguageSettings, PublicSettings} from "../types/settings.ts";

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

    if (error.response?.status && error.response.status >= 500) {
        return "The server returned an error. Check the backend logs and try again.";
    }

    if (error.code === "ERR_NETWORK") {
        return "Unable to reach the API. Confirm the local stack is running and the hostnames are configured.";
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

export const fetchDashboardPreferences = async () => {
    const response = await adminApiClient.get<DashboardPreferences>(
        "/admin/dashboard/preferences",
    );
    return response.data;
};

export const updateDashboardPreferences = async (payload: DashboardPreferences) => {
    const response = await adminApiClient.patch<DashboardPreferences>(
        "/admin/dashboard/preferences",
        payload,
    );
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

export const updateProductLanguageSettings = async (
    payload: ProductLanguageSettingsUpdate,
) => {
    const response = await adminApiClient.patch<ProductLanguageSettings>(
        "/admin/settings/languages",
        payload,
    );
    return response.data;
};

export const backfillProductTranslations = async () => {
    const response = await adminApiClient.post<ProductTranslationBackfillResponse>(
        "/admin/translations/backfill",
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
    tags: form.tags
        .split(",")
        .map((tag) => tag.trim().toLowerCase())
        .filter(Boolean),
    translations: form.translations
        .map((translation) => ({
            language_code: translation.language_code.trim().toLowerCase(),
            product_name: translation.product_name.trim(),
            product_description: translation.product_description.trim(),
        }))
        .filter(
            (translation) =>
                translation.language_code &&
                translation.product_name &&
                translation.product_description,
        ),
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

export const updateOrderNotes = async (orderId: string, adminNotes: string) => {
    await adminApiClient.patch(`/orders/${orderId}/notes`, {
        admin_notes: adminNotes || null,
    });
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
