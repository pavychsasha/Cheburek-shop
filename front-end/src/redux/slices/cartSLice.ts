import {createAsyncThunk, createSlice} from "@reduxjs/toolkit";
import axios from "axios";

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
}

const initialState: ICartState = {
    total_price: 0,
    total_count: 0,
    items: [],
    fetchCartStatus: '',
    addItemStatus: ''
};


const baseUrl = 'http://localhost:8000/api/v1';

const findItem = (items: IItem[], id: string) => items.find(item => item.product_id === id);

const updateTotals = (state: ICartState) => {
    state.total_price = state.items.reduce((sum, item) => sum + (item.price * item.count), 0);
    state.total_count = state.items.reduce((count, item) => count + item.count, 0);
}

export const fetchCart = createAsyncThunk('cart/fetchCart',
    async () => {
        const {data} = await axios.get(baseUrl + '/cart/', {withCredentials: true});
        console.log(data);
        return data;
    }
)

export const addItemToBackend = createAsyncThunk('cart/addItem',
    async (item: IItem) => {
    const patchParams = {
        product_id: item.product_id,
        count: 1
    }
        await axios.patch(baseUrl + '/cart/add', patchParams, {withCredentials: true})
        return item;
    }
)

const cartSlice = createSlice({
    name: 'cart',
    initialState,
    reducers: {
        addItem(state, action) {
            const existingItem = findItem(state.items, action.payload.product_id);
            if (existingItem) {
                existingItem.count += 1;
            } else {
                state.items.push({
                    ...action.payload,
                    count: 1
                });
            }
            updateTotals(state);
        },
        removeItem(state, action) {
            const existingItem = findItem(state.items, action.payload);
            if (existingItem) {
                if (existingItem.count > 1) {
                    existingItem.count -= 1;
                } else {
                    state.items = state.items.filter(item => item.product_id !== action.payload);
                }
                updateTotals(state);
            }
        },
        deleteItem(state, action) {
            const existingItem = findItem(state.items, action.payload);
            if (existingItem) {
                state.items = state.items.filter(item => item.product_id !== action.payload);
                updateTotals(state);
            }
        },
        clearCart(state) {
            state.items = [];
            updateTotals(state);
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchCart.pending, (state) => {
                state.fetchCartStatus = 'loading';
                state.items = [];
            })
            .addCase(fetchCart.fulfilled, (state, action) => {
                state.items = action.payload.items;
                state.total_count = action.payload.total_count;
                state.total_price = action.payload.total_price;
                state.fetchCartStatus = 'success';
            })
            .addCase(fetchCart.rejected, (state) => {
                state.fetchCartStatus = 'error';
                state.items = [];
            })
        builder
            .addCase(addItemToBackend.pending, (state) => {
                state.addItemStatus = 'loading';
            })
            .addCase(addItemToBackend.fulfilled, (state, action) => {
                const existingItem = findItem(state.items, action.payload.product_id);
                console.log(action.payload)
                if (existingItem) {
                    existingItem.count += 1;
                } else {
                    state.items.push({
                        ...action.payload,
                        count: 1
                    });
                }
                state.addItemStatus = 'success';
                updateTotals(state);
            })
            .addCase(addItemToBackend.rejected, (state) => {
                state.addItemStatus = 'error';
            })
    }
});

export const {
    addItem,
    removeItem,
    deleteItem,
    clearCart
} = cartSlice.actions;

export default cartSlice.reducer;
