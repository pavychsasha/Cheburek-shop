import './App.scss'
import Header from "./components/common/Header/Header.tsx";
import Home from "./components/pages/Home/Home.tsx";
import {Route, Routes} from "react-router-dom";
import NotFound from "./components/pages/NotFound/NotFound.tsx";
import Cart from "./components/pages/Cart/Cart.tsx";
//import { useSelector, useDispatch } from 'react-redux'
//import {RootState} from "./redux/store.ts";

function App() {
    //const count = useSelector((state: RootState) => state.filter.value)
    //const dispatch = useDispatch()


    return (
        <div className={'app__wrapper'}>
            <Header/>
            <Routes>
                <Route path={'/'} element={<Home/>}/>
                <Route path={'/cart'} element={<Cart/>}/>
                <Route path={'*'} element={<NotFound/>}/>
            </Routes>

        </div>
    )
}

export default App
