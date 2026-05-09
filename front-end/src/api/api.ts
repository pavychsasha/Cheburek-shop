import axios from "axios";

const defaultApiHost =
    window.location.hostname === "app.local.cheburek-shop.com"
        ? "api.local.cheburek-shop.com"
        : "localhost";

export const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? `http://${defaultApiHost}:8091/api/v1`;

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
});

export const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? {Authorization: `Bearer ${token}`} : undefined;
};
