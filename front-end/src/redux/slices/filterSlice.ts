import {createSlice} from "@reduxjs/toolkit";

interface ISortType {
    name: string;
    sortType: string;
    sortOrder: string;
}

interface IFilterState {
    category: string;
    sort: ISortType;
    searchValue: string;
}

const initialState: IFilterState = {
    category: 'Все',
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