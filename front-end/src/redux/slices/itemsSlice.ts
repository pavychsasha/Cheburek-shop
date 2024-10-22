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
            searchValue
        } = params
        const {data} = await axios.get(
            `${baseUrl}/products/search?name=${searchValue}&category=${categoryParam}&sort_by=${sortBy}&order=${orderBy}&page=1&per_page=8`
        );
        return data.products;
    })

const initialState: IItemsState = {
    items: [],
    status: ''
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
                state.items = action.payload;
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
