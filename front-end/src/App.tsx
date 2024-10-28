import './App.scss';
import Header from "./components/common/Header/Header.tsx";
import Home from "./components/pages/Home/Home.tsx";
import {Route, Routes, useLocation} from "react-router-dom";
import NotFound from "./components/pages/NotFound/NotFound.tsx";
import Cart from "./components/pages/Cart/Cart.tsx";
import Login from "./components/pages/Auth/Login/Login.tsx";
import Register from "./components/pages/Auth/Register/Register.tsx";
import {useDispatch} from "react-redux";
import React from "react";
import {fetchCart} from "./redux/slices/cartSLice.ts";
import axios from "axios";
import {setIsAuth} from "./redux/slices/authSlice.ts";

const App = () => {
    const dispatch = useDispatch();

    React.useEffect(() => {
        axios.get('http://localhost:8000/api/v1/users/me', {withCredentials: true}).then(response => {
            if (response.status === 200) {
                dispatch(setIsAuth(true));
            }
        })
    }, [])

    React.useEffect(() => {
        dispatch(fetchCart());
    }, [dispatch]);

    const location = useLocation();

    const shouldShowHeader = !['/login', '/register'].includes(location.pathname);

    return (
        <div className={shouldShowHeader ? 'app__wrapper' : ''}>
            {shouldShowHeader && <Header/>}
            <Routes>
                <Route path={'/'} element={<Home/>}/>
                <Route path={'/cart'} element={<Cart/>}/>
                <Route path={'/login'} element={<Login/>}/>
                <Route path={'/register'} element={<Register/>}/>
                <Route path={'*'} element={<NotFound/>}/>
            </Routes>
        </div>
    );
};

export default App;
