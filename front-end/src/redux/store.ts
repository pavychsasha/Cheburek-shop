import {configureStore} from '@reduxjs/toolkit'
import filterReducer from "./slices/filterSlice";
import authSlice from "./slices/authSlice.ts";
import cartSLice from "./slices/cartSLice.ts";
import itemsSLice from "./slices/itemsSlice.ts";
import langSlice from "./slices/langSlice.ts";
import settingsSlice from "./slices/settingsSlice.ts";

export const store = configureStore({
    reducer: {
        filter: filterReducer,
        auth: authSlice,
        cart: cartSLice,
        items: itemsSLice,
        lang: langSlice,
        settings: settingsSlice
    },
})

export type RootState = ReturnType<typeof store.getState>

export type AppDispatch = typeof store.dispatch
