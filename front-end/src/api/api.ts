import axios from "axios";

export const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8091/api/v1";

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
});

export const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? {Authorization: `Bearer ${token}`} : undefined;
};
