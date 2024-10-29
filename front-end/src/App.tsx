import './App.scss';
import Header from "./components/common/Header/Header.tsx";
import Home from "./components/pages/Home/Home.tsx";
import {Route, Routes, useLocation} from "react-router-dom";
import NotFound from "./components/pages/NotFound/NotFound.tsx";
import Cart from "./components/pages/Cart/Cart.tsx";
import Login from "./components/pages/Auth/Login/Login.tsx";
import Register from "./components/pages/Auth/Register/Register.tsx";
import {useDispatch, useSelector} from "react-redux";
import React, {useRef} from "react";
import {fetchCart} from "./redux/slices/cartSLice.ts";
import axios from "axios";
import {setIsAuth} from "./redux/slices/authSlice.ts";
import {RootState} from "./redux/store.ts";
import {useTranslation} from "react-i18next";
import {setIsLanguageSet} from "./redux/slices/langSlice.ts";

const App = () => {
    const dispatch = useDispatch();

    const {i18n} = useTranslation();

    const isAuthorized = useSelector((state: RootState) => state.auth.isAuthorized);
    const isLanguageSet = useSelector((state: RootState) => state.lang.isLanguageSet);

    React.useEffect(() => {
        const fetchLanguage = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/v1/languages/current_language', {withCredentials: true});
                if (response.data.language !== 'en') {
                    await axios.post('http://localhost:8000/api/v1/languages/change_language?language=en', null, {withCredentials: true});
                    i18n.changeLanguage('en');
                }
            } catch (error) {
                console.error("Error fetching or changing language:", error);
            } finally {
                dispatch(setIsLanguageSet(true));
            }
        };

        fetchLanguage();
    }, []);

    React.useEffect(() => {
        axios.get('http://localhost:8000/api/v1/users/me', {withCredentials: true}).then(response => {
            if (response.status === 200) {
                dispatch(setIsAuth(true));
            }
        })
    }, [])

    React.useEffect(() => {
        if (isLanguageSet) {
            dispatch(fetchCart());
        }
    }, [dispatch, isAuthorized, i18n.language, isLanguageSet]);

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
