import {createSlice} from "@reduxjs/toolkit";
import {IFilterState} from "../../types/filter.ts";

const initialState: IFilterState = {
    category: 'Все',
    sort: {
        nameUa: 'алфавітом',
        nameEn: 'alphabet',
        sortType: 'name',
        sortOrder: 'asc'
    },
    searchValue: ''
};

const filterSlice = createSlice({
    name: 'filters',
    initialState,
    reducers: {
        setCategory(state, action) {
            state.category = action.payload;
        },
        setSort(state, action) {
            state.sort = action.payload;
        },
        setSearchValue(state, action) {
            state.searchValue = action.payload;
        }
    }
});

export const {
    setCategory,
    setSort,
    setSearchValue
} = filterSlice.actions;

export default filterSlice.reducer;