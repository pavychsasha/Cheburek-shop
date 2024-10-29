import {createSlice} from "@reduxjs/toolkit";

const initialState = {
    isLanguageSet: false,
}

const langSlice = createSlice({
    name: 'lang',
    initialState,
    reducers: {
        setIsLanguageSet(state, action){
            state.isLanguageSet = action.payload;
        }
    }
});

export const {
    setIsLanguageSet,
} = langSlice.actions;

export default langSlice.reducer;