import {createSlice} from "@reduxjs/toolkit";
import {IAuth} from "../../types/auth.ts";

const initialState: IAuth = {
    isAuthorized: false,
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setIsAuth(state, action){
            state.isAuthorized = action.payload;
        }
    }
});

export const {
    setIsAuth,
 } = authSlice.actions;

export default authSlice.reducer;