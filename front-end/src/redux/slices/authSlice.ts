import {createSlice} from "@reduxjs/toolkit";

interface IAuth {
    isAuthorized: boolean;
    bearerToken: string;
}

const initialState: IAuth = {
    isAuthorized: true,
    bearerToken: "",
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setIsAuth(state, action){
            state.bearerToken = action.payload;
            state.isAuthorized = action.payload;
        }
    }
});

export const {
    setIsAuth,
 } = authSlice.actions;

export default authSlice.reducer;