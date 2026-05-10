import {createAsyncThunk, createSlice} from "@reduxjs/toolkit";
import {IParams} from "../../types/api.ts";
import {IItemsState} from "../../types/state.ts";
import {apiClient} from "../../api/api.ts";

export const fetchItems = createAsyncThunk('items/fetchItemsStatus',
    async (params: IParams) => {

        //Setting parameters for get request /products/search
        const {
            sortBy,
            orderBy,
            categoryParam,
            searchValue,
            currentPage
        } = params
        const {data} = await apiClient.get('/products/search/', {
            params: {
                name: searchValue,
                category: categoryParam,
                sort_by: sortBy,
                order: orderBy,
                page: currentPage,
                per_page: 8,
            },
        });
        return data;
    })

const initialState: IItemsState = {
    items: [],
    status: 'idle',
    pagesCount: 1,
    currentRequestId: undefined,
    lastError: undefined,
};

const itemsSlice = createSlice({
    name: 'items',
    initialState,
    reducers: {
        setItems(state, action) {
            state.items = action.payload;
        }
    },

    //Checking for status of fetching
    extraReducers: (builder) => {
        builder
            .addCase(fetchItems.pending, (state, action) => {
                state.currentRequestId = action.meta.requestId;
                state.status = state.items.length > 0 ? 'refreshing' : 'loading';
                state.lastError = undefined;
            })
            .addCase(fetchItems.fulfilled, (state, action) => {
                if (state.currentRequestId !== action.meta.requestId) {
                    return;
                }
                state.status = 'success';
                state.items = action.payload.products;
                state.pagesCount = action.payload.pages;
                state.currentRequestId = undefined;
            })
            .addCase(fetchItems.rejected, (state, action) => {
                if (state.currentRequestId !== action.meta.requestId) {
                    return;
                }
                state.status = state.items.length > 0 ? 'success' : 'error';
                state.lastError = action.error.message;
                state.currentRequestId = undefined;
            })
    },
});

export const {
    setItems
} = itemsSlice.actions;

export default itemsSlice.reducer;
