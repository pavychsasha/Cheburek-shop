import {createAsyncThunk, createSlice} from "@reduxjs/toolkit";
import {apiClient, getAuthHeaders} from "../../api/api.ts";

interface IItem {
    product_id: string;
    name: string;
    price: number;
    image_src: string;
    count: number;
}

interface ICartState {
    total_price: number;
    total_count: number;
    items: IItem[];
    fetchCartStatus: string;
    addItemStatus: string;
    subtractItemStatus: string;
    deleteItemStatus: string;
    clearCartStatus: string;
}

const initialState: ICartState = {
    total_price: 0,
    total_count: 0,
    items: [],
    fetchCartStatus: '',
    addItemStatus: '',
    subtractItemStatus: '',
    deleteItemStatus: '',
    clearCartStatus: ''
};

type CartStatusField =
    | 'fetchCartStatus'
    | 'addItemStatus'
    | 'subtractItemStatus'
    | 'deleteItemStatus'
    | 'clearCartStatus';

// Helper function to find item by product ID
const findItem = (items: IItem[], id: string) => items.find(item => item.product_id === id);

// Helper function to update total price and count
const updateTotals = (state: ICartState) => {
    state.total_price = state.items.reduce((sum, item) => sum + (item.price * item.count), 0);
    state.total_count = state.items.reduce((count, item) => count + item.count, 0);
};

// Helper function to handle API status updates
const updateStatus = (state: ICartState, field: CartStatusField, status: string) => {
    state[field] = status;
};

// Async Thunks for API calls
export const fetchCart = createAsyncThunk('cart/fetchCart', async () => {
    const {data} = await apiClient.get('/cart/', {headers: getAuthHeaders()});
    return data;
});

export const addItemToBackend = createAsyncThunk('cart/addItem', async (item: IItem) => {
    await apiClient.patch('/cart/add', {product_id: item.product_id, count: 1});
    return item;
});

export const subtractItemFromBackend = createAsyncThunk('cart/subtractItem', async (product_id: string) => {
    await apiClient.patch('/cart/subtract_product', {product_id, count: 1});
    return product_id;
});

export const deleteItemFromBackend = createAsyncThunk('cart/deleteItem', async (product_id: string) => {
    await apiClient.delete(`/cart/product/${product_id}`);
    return product_id;
});

export const clearCartFromBackend = createAsyncThunk('cart/clearCart', async () => {
    await apiClient.delete('/cart/');
});

// Cart Slice
const cartSlice = createSlice({
    name: 'cart',
    initialState,
    reducers: {

    },
    extraReducers: (builder) => {
        // Fetch Cart
        builder
            .addCase(fetchCart.pending, (state) => updateStatus(state, 'fetchCartStatus', 'loading'))
            .addCase(fetchCart.fulfilled, (state, action) => {
                state.items = action.payload.items;
                state.total_count = action.payload.total_count;
                state.total_price = action.payload.total_price;
                updateStatus(state, 'fetchCartStatus', 'success');
            })
            .addCase(fetchCart.rejected, (state) => updateStatus(state, 'fetchCartStatus', 'error'));

        // Add Item
        builder
            .addCase(addItemToBackend.pending, (state) => updateStatus(state, 'addItemStatus', 'loading'))
            .addCase(addItemToBackend.fulfilled, (state, action) => {
                const existingItem = findItem(state.items, action.payload.product_id);
                if (existingItem) {
                    existingItem.count += 1;
                } else {
                    state.items.push({...action.payload, count: 1});
                }
                updateStatus(state, 'addItemStatus', 'success');
                updateTotals(state);
            })
            .addCase(addItemToBackend.rejected, (state) => updateStatus(state, 'addItemStatus', 'error'));

        // Subtract Item
        builder
            .addCase(subtractItemFromBackend.pending, (state) => updateStatus(state, 'subtractItemStatus', 'loading'))
            .addCase(subtractItemFromBackend.fulfilled, (state, action) => {
                const existingItem = findItem(state.items, action.payload);
                if (existingItem) {
                    if (existingItem.count > 1) {
                        existingItem.count -= 1;
                    } else {
                        state.items = state.items.filter(item => item.product_id !== action.payload);
                    }
                    updateStatus(state, 'subtractItemStatus', 'success');
                    updateTotals(state);
                }
            })
            .addCase(subtractItemFromBackend.rejected, (state) => updateStatus(state, 'subtractItemStatus', 'error'));

        // Delete Item
        builder
            .addCase(deleteItemFromBackend.pending, (state) => updateStatus(state, 'deleteItemStatus', 'loading'))
            .addCase(deleteItemFromBackend.fulfilled, (state, action) => {
                state.items = state.items.filter(item => item.product_id !== action.payload);
                updateStatus(state, 'deleteItemStatus', 'success');
                updateTotals(state);
            })
            .addCase(deleteItemFromBackend.rejected, (state) => updateStatus(state, 'deleteItemStatus', 'error'));

        // Clear Cart
        builder
            .addCase(clearCartFromBackend.pending, (state) => updateStatus(state, 'clearCartStatus', 'loading'))
            .addCase(clearCartFromBackend.fulfilled, (state) => {
                state.items = [];
                state.total_count = 0;
                state.total_price = 0;
                updateStatus(state, 'clearCartStatus', 'success');
            })
            .addCase(clearCartFromBackend.rejected, (state) => updateStatus(state, 'clearCartStatus', 'error'));
    }
});

export default cartSlice.reducer;
