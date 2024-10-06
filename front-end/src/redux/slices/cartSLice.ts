import {createAsyncThunk, createSlice} from "@reduxjs/toolkit";
import axios from "axios";

interface IItem {
    id: string;
    name: string;
    price: number;
    imageSrc: string;
    count: number;
}

interface ICartState {
    totalPrice: number;
    totalCount: number;
    items: IItem[];
    fetchCartStatus: string;
    addItemStatus: string;
}

const initialState: ICartState = {
    totalPrice: 0,
    totalCount: 0,
    items: [],
    fetchCartStatus: '',
    addItemStatus: ''
};


const baseUrl = 'http://localhost:8000/api/v1';

const findItem = (items: IItem[], id: string) => items.find(item => item.id === id);

const updateTotals = (state: ICartState) => {
    state.totalPrice = state.items.reduce((sum, item) => sum + (item.price * item.count), 0);
    state.totalCount = state.items.reduce((count, item) => count + item.count, 0);
}

interface IPatchParams {
    product_id: string;
    count: number;
}

export const fetchCart = createAsyncThunk('cart/fetchCart',
    async () => {
        const {data} = await axios.get(baseUrl + '/cart/');
        return data;
    }
)

export const addItemToBackend = createAsyncThunk('cart/addItem',
    async (patchParams: IPatchParams) => {
        const {data} = await axios.patch(baseUrl + '/cart/add', patchParams, {withCredentials: true})
        return data;
    }
)

const cartSlice = createSlice({
    name: 'cart',
    initialState,
    reducers: {
        addItem(state, action) {
            const existingItem = findItem(state.items, action.payload.id);
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
                    state.items = state.items.filter(item => item.id !== action.payload);
                }
                updateTotals(state);
            }
        },
        deleteItem(state, action) {
            const existingItem = findItem(state.items, action.payload);
            if (existingItem) {
                state.items = state.items.filter(item => item.id !== action.payload);
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
                state.items = action.payload;
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
                const existingItem = findItem(state.items, action.payload.id);
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
