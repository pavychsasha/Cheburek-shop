import {createSlice} from "@reduxjs/toolkit";
import {IAuth} from "../../types/auth.ts";

const initialState: IAuth = {
    isAuthorized: true,
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setIsAuth(state, action){
            //const {isAuthorized, bearerToken} = action.payload;
            //localStorage.setItem('bearerToken', bearerToken);
            state.isAuthorized = action.payload;
        }
    }
});

export const {
    setIsAuth,
 } = authSlice.actions;

export default authSlice.reducer;