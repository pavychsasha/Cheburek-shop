import { createSlice } from "@reduxjs/toolkit";

interface IItem {
    id: number;
    name: string;
    price: number;
    imageUrl: string;
    count: number;
}

interface ICartState {
    totalPrice: number;
    totalCount: number;
    items: IItem[];
}

const initialState: ICartState = {
    totalPrice: 0,
    totalCount: 0,
    items: []
};

const findItem = (items: IItem[], id: number) => items.find(item => item.id === id);

const updateTotals = (state: ICartState) => {
    state.totalPrice = state.items.reduce((sum, item) => sum + (item.price * item.count), 0);
    state.totalCount = state.items.reduce((count, item) => count + item.count, 0);
}

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
    }
});

export const {
    addItem,
    removeItem,
    deleteItem,
    clearCart
} = cartSlice.actions;

export default cartSlice.reducer;
