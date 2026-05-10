import './App.scss';
import Header from "./components/common/Header/Header.tsx";
import Home from "./components/pages/Home/Home.tsx";
import {Route, Routes, useLocation} from "react-router-dom";
import NotFound from "./components/pages/NotFound/NotFound.tsx";
import Cart from "./components/pages/Cart/Cart.tsx";
import Login from "./components/pages/Auth/Login/Login.tsx";
import Register from "./components/pages/Auth/Register/Register.tsx";
import React, {Suspense, useEffect} from "react";
import {fetchCart} from "./redux/slices/cartSLice.ts";
import {setIsAuth} from "./redux/slices/authSlice.ts";
import {useTranslation} from "react-i18next";
import {setIsLanguageSet} from "./redux/slices/langSlice.ts";
import Order from "./components/pages/Order/Order.tsx";
import {apiClient, getAuthHeaders} from "./api/api.ts";
import {useAppDispatch, useAppSelector} from "./redux/hooks.ts";
import {fetchPublicSettings} from "./redux/slices/settingsSlice.ts";
import Seo from "./components/common/Seo/Seo.tsx";

const isAdminHost = window.location.hostname === "admin.local.cheburek-shop.com";
const AdminApp = React.lazy(() => import("./admin/AdminApp.tsx"));

const StorefrontApp = () => {
    const dispatch = useAppDispatch();

    const {i18n} = useTranslation();

    const isAuthorized = useAppSelector((state) => state.auth.isAuthorized);
    const isLanguageSet = useAppSelector((state) => state.lang.isLanguageSet);

    React.useEffect(() => {
        const fetchLanguage = async () => {
            try {
                const response = await apiClient.get('/languages/current_language');
                if (response.data.language !== 'en') {
                    await apiClient.post('/languages/change_language', null, {params: {language: 'en'}});
                    await i18n.changeLanguage('en');
                }
            } catch (error) {
                console.error("Error fetching or changing language:", error);
            } finally {
                dispatch(setIsLanguageSet(true));
            }
        };

        fetchLanguage();
    }, [dispatch, i18n]);

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('token');

            if (!token) {
                dispatch(setIsAuth(false));
                return;
            }

            try {
                const res = await apiClient.get('/users/me', {headers: getAuthHeaders()});
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

        checkAuth();
    }, [dispatch]);

    React.useEffect(() => {
        if (isLanguageSet) {
            dispatch(fetchCart());
        }
    }, [dispatch, isAuthorized, i18n.language, isLanguageSet]);

    const location = useLocation();

    const shouldShowHeader = !['/login', '/register'].includes(location.pathname);
    const storefrontDescription =
        "Order hot chebureks, pies, snacks, and drinks from Cheburek Shop with a fast local checkout experience.";
    const restaurantJsonLd = {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        name: "Cheburek Shop",
        servesCuisine: ["Ukrainian", "Street food"],
        url: window.location.origin,
        acceptsReservations: false,
        hasMenu: `${window.location.origin}/`,
    };

    return (
        <div className={shouldShowHeader ? 'app__wrapper' : ''}>
            <Seo
                title="Cheburek Shop | Hot Chebureks, Pies, Snacks, and Drinks"
                description={storefrontDescription}
                canonicalPath={location.pathname}
                jsonLd={restaurantJsonLd}
            />
            {shouldShowHeader && <Header/>}
            <Routes>
                <Route path={'/'} element={<Home/>}/>
                <Route path={'/cart'} element={<Cart/>}/>
                <Route path={'/login'} element={<Login/>}/>
                <Route path={'/register'} element={<Register/>}/>
                <Route path={'/order'} element={<Order/>}/>
                <Route path={'*'} element={<NotFound/>}/>
            </Routes>
        </div>
    );
};

const App = () => {
    const dispatch = useAppDispatch();

    useEffect(() => {
        dispatch(fetchPublicSettings());
    }, [dispatch]);

    if (isAdminHost) {
        return (
            <Suspense fallback={<div className="app__loading">Loading admin portal.</div>}>
                <Seo
                    title="Cheburek Shop Admin"
                    description="Private catalog and order management workspace."
                    noindex
                />
                <AdminApp/>
            </Suspense>
        );
    }

    return <StorefrontApp/>;
};

export default App;
