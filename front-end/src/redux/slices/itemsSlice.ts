import {createAsyncThunk, createSlice} from "@reduxjs/toolkit";
import axios from "axios";
import {IParams} from "../../types/api.ts";
import {IItemsState} from "../../types/state.ts";

const baseUrl = 'http://localhost:8000/api/v1';

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
        const {data} = await axios.get(
            `${baseUrl}/products/search?name=${searchValue}&category=${categoryParam}&sort_by=${sortBy}&order=${orderBy}&page=${currentPage}&per_page=8`, {withCredentials: true}
        );
        return data;
    })

const initialState: IItemsState = {
    items: [],
    status: '',
    pagesCount: 1
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
            .addCase(fetchItems.pending, (state) => {
                state.status = 'loading';
                state.items = [];
            })
            .addCase(fetchItems.fulfilled, (state, action) => {
                state.status = 'success';
                state.items = action.payload.products;
                state.pagesCount = action.payload.pages;
            })
            .addCase(fetchItems.rejected, (state) => {
                state.status = 'error';
                state.items = [];
            })
    },
});

export const {
    setItems
} = itemsSlice.actions;

export default itemsSlice.reducer;
