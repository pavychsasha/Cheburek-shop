import {configureStore} from '@reduxjs/toolkit'
import filterReducer from "./slices/filterSlice";
import authSlice from "./slices/authSlice.ts";
import cartSLice from "./slices/cartSLice.ts";

export const store = configureStore({
    reducer: {
        filter: filterReducer,
        auth: authSlice,
        cart: cartSLice
    },
})

export type RootState = ReturnType<typeof store.getState>

export type AppDispatch = typeof store.dispatch