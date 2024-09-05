import {createSlice} from "@reduxjs/toolkit";

interface SortType {
    name: string;
    sortType: string;
    sortOrder: string;
}

interface FilterState {
    categoryId: number;
    sort: SortType;
    searchValue: string;
}

const initialState: FilterState = {
    categoryId: 0,
    sort: {
        name: 'алфавітом',
        sortType: 'name',
        sortOrder: 'asc'

    },
    searchValue: ''
};

const filterSlice = createSlice({
    name: 'filters',
    initialState,
    reducers: {
        setCategoryId(state, action) {
            state.categoryId = action.payload;
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
    setCategoryId,
    setSort,
    setSearchValue
} = filterSlice.actions;

export default filterSlice.reducer;