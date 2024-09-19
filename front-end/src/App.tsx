import './App.scss'
import Header from "./components/common/Header/Header.tsx";
import Home from "./components/pages/Home/Home.tsx";
import {Route, Routes, useLocation} from "react-router-dom";
import NotFound from "./components/pages/NotFound/NotFound.tsx";
import Cart from "./components/pages/Cart/Cart.tsx";
import Login from "./components/pages/Auth/Login/Login.tsx";
import Register from "./components/pages/Auth/Register/Register.tsx";

const App = () => {
    const location = useLocation();

    const noHeaderRoutes = ['/login', '/register'];

    return (
        <div className={!noHeaderRoutes.includes(location.pathname) ? 'app__wrapper' : ''}>
            {!noHeaderRoutes.includes(location.pathname) && <Header/>}
            <Routes>
                <Route path={'/'} element={<Home/>}/>
                <Route path={'/cart'} element={<Cart/>}/>
                <Route path={'/login'} element={<Login/>}/>
                <Route path={'/register'} element={<Register/>}/>
                <Route path={'*'} element={<NotFound/>}/>
            </Routes>
        </div>
    );
}

export default App
