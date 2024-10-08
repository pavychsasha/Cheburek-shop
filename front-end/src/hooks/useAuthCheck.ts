import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import axios from 'axios';
import { setIsAuth } from "../redux/slices/authSlice";
import { RootState } from "../redux/store";

export const useAuthCheck = () => {
    const dispatch = useDispatch();
    const isAuthorized = useSelector((state: RootState) => state.auth.isAuthorized);

    const checkAuth = async () => {
        try {
            const res = await axios.get('http://localhost:8000/api/v1/users/me', { withCredentials: true });
            if (res.data) {
                dispatch(setIsAuth(true));
            } else {
                dispatch(setIsAuth(false));
            }
        } catch (error) {
            console.error('Authentication check failed', error);
            dispatch(setIsAuth(false));
        }
    };

    useEffect(() => {
        checkAuth();
    }, [dispatch]);

    return isAuthorized;
};
