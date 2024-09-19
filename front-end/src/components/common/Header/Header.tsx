import cheburekLogo from "../../../assets/cheburekLogo.png";
import {CiShoppingCart} from "react-icons/ci";

import styles from './Header.module.scss';
import Searchbar from "../Searchbar/Searchbar.tsx";
import {NavLink} from "react-router-dom";
import {useDispatch, useSelector} from "react-redux";
import {RootState} from '../../../redux/store.ts'
import {setSearchValue} from "../../../redux/slices/filterSlice.ts";


const Header = () => {
    const searchValue = useSelector((state: RootState) => state.filter.searchValue);
    const {totalPrice, totalCount} = useSelector((state: RootState) => state.cart)

    const dispatch = useDispatch();

    const onChangeSearch = (value: string) => {
        dispatch(setSearchValue(value));
    }

    return (
        <header>
            <NavLink className={styles.link} to={'/'}>
                <div className={styles.logo__and__name}>
                    <img src={cheburekLogo} className={styles.logo} alt="logo"/>
                    <div className={styles.name__and__slogan}>
                        <h1>Пиріжечки&Чебуречки</h1>
                        <p>Найсмачніше для найкращих</p>
                    </div>
                </div>
            </NavLink>
            <Searchbar searchValue={searchValue}
                       onChangeSearch={onChangeSearch}/>
            <div className={styles.btn}>
                <NavLink to="/cart">
                    <span>{totalPrice} ₴</span>
                    <span className={styles.delim}>|</span>
                    <CiShoppingCart/>
                    <span>{totalCount}</span>
                </NavLink>
            </div>
        </header>)
}

export default Header;

