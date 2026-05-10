import {createAsyncThunk, createSlice, PayloadAction} from "@reduxjs/toolkit";

import {apiClient} from "../../api/api.ts";
import type {CurrencySettings, PublicSettings} from "../../types/settings.ts";
import {fallbackCurrencySettings} from "../../utils/currency.ts";

interface SettingsState {
    currency: CurrencySettings;
    categoryMedia: Record<string, string>;
    selectedCurrency: string;
    status: "idle" | "loading" | "success" | "error";
    error: string;
}

const getStoredCurrency = () => {
    if (typeof window === "undefined") {
        return fallbackCurrencySettings.default_currency;
    }
    return localStorage.getItem("displayCurrency") || fallbackCurrencySettings.default_currency;
};

const initialState: SettingsState = {
    currency: fallbackCurrencySettings,
    categoryMedia: {},
    selectedCurrency: getStoredCurrency(),
    status: "idle",
    error: "",
};

export const fetchPublicSettings = createAsyncThunk(
    "settings/fetchPublicSettings",
    async () => {
        const response = await apiClient.get<PublicSettings>("/settings/public");
        return response.data;
    },
);

const settingsSlice = createSlice({
    name: "settings",
    initialState,
    reducers: {
        setSelectedCurrency: (state, action: PayloadAction<string>) => {
            const nextCurrency = action.payload;
            if (!state.currency.supported_currencies.includes(nextCurrency)) {
                return;
            }
            state.selectedCurrency = nextCurrency;
            localStorage.setItem("displayCurrency", nextCurrency);
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchPublicSettings.pending, (state) => {
                state.status = "loading";
                state.error = "";
            })
            .addCase(fetchPublicSettings.fulfilled, (state, action) => {
                state.currency = action.payload.currency;
                state.categoryMedia = action.payload.category_media || {};
                state.status = "success";
                if (!state.currency.supported_currencies.includes(state.selectedCurrency)) {
                    state.selectedCurrency = state.currency.default_currency;
                    localStorage.setItem("displayCurrency", state.selectedCurrency);
                }
            })
            .addCase(fetchPublicSettings.rejected, (state) => {
                state.status = "error";
                state.error = "Unable to load display settings.";
            });
    },
});

export const {setSelectedCurrency} = settingsSlice.actions;

export default settingsSlice.reducer;
