import axios from "axios";
import type {IItem} from "../types/items.ts";

const defaultApiHost =
    window.location.hostname === "app.local.cheburek-shop.com" ||
    window.location.hostname === "admin.local.cheburek-shop.com"
        ? "api.local.cheburek-shop.com"
        : "localhost";

const resolveApiBaseUrl = () => {
    const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL;
    if (!configuredApiBaseUrl) {
        return defaultApiHost === "localhost"
            ? "http://localhost:8091/api/v1"
            : `http://${defaultApiHost}/api/v1`;
    }

    try {
        const apiUrl = new URL(configuredApiBaseUrl);
        const isLocalhostFallback =
            window.location.hostname === "localhost" ||
            window.location.hostname === "127.0.0.1";
        if (isLocalhostFallback && apiUrl.hostname === "api.local.cheburek-shop.com") {
            apiUrl.hostname = window.location.hostname;
            if (!apiUrl.port) {
                apiUrl.port = "8091";
            }
        }
        return apiUrl.toString().replace(/\/$/, "");
    } catch {
        return configuredApiBaseUrl;
    }
};

export const API_BASE_URL = resolveApiBaseUrl();

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
});

export const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? {Authorization: `Bearer ${token}`} : undefined;
};

export const trackVisit = async (path: string) => {
    await apiClient.post("/analytics/visit", {path});
};

export const fetchSimilarProducts = async (productIds: string[], limit = 4) => {
    if (productIds.length === 0) {
        return [];
    }

    const params = new URLSearchParams();
    productIds.forEach((productId) => params.append("product_ids", productId));
    params.set("limit", String(limit));

    const response = await apiClient.get<IItem[]>(`/products/similar?${params.toString()}`);
    return response.data;
};
