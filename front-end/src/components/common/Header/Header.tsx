import cheburekLogo from "../../../assets/cheburekLogo.png";
import {CiShoppingCart} from "react-icons/ci";
import styles from './Header.module.scss';
import Searchbar from "../Searchbar/Searchbar.tsx";
import {NavLink, useLocation} from "react-router-dom";
import {useDispatch, useSelector} from "react-redux";
import {RootState} from '../../../redux/store.ts'
import {setSearchValue} from "../../../redux/slices/filterSlice.ts";
import {FaUserCircle} from "react-icons/fa";
import {useTranslation} from "react-i18next";
import LangSelector from "../LangSelector/LangSelector.tsx";
import {RiLogoutBoxRLine, RiLogoutCircleRFill} from "react-icons/ri";
import axios from "axios";
import {setIsAuth} from "../../../redux/slices/authSlice.ts";


const Header = () => {
    const isAuthorized = useSelector((state: RootState) => state.auth.isAuthorized)
    const searchValue = useSelector((state: RootState) => state.filter.searchValue);
    const {total_price, total_count} = useSelector((state: RootState) => state.cart)

    const dispatch = useDispatch();

    const location = useLocation();

    const [t] = useTranslation('global');

    const onChangeSearch = (value: string) => {
        dispatch(setSearchValue(value));
    }

    return (
        <header>
            <NavLink className={styles.link} to={'/'}>
                <div className={styles.logo__and__name}>
                    <img src={cheburekLogo} className={styles.logo} alt="logo"/>
                    <div className={styles.name__and__slogan}>
                        <h1>{t("header.logo")}</h1>
                        <p>{t('header.slogan')}</p>
                    </div>
                </div>
            </NavLink>
            {location.pathname !== '/cart' && <Searchbar searchValue={searchValue}
                                                         onChangeSearch={onChangeSearch}
            />}
            <div className={styles.left}>
                <LangSelector/>
                {
                    isAuthorized
                        ?
                        <a>
                            <RiLogoutCircleRFill onClick={() =>
                            {
                                axios.post("http://localhost:8000/api/v1/auth/logout", {},{withCredentials: true});
                                dispatch(setIsAuth(false));
                            }} className={styles.user}/>
                        </a>
                        :
                        <NavLink className={styles.link} to="/register">
                            <FaUserCircle className={styles.user}/>
                        </NavLink>
                }

                <div className={styles.btn}>
                    <NavLink className={styles.link} to="/cart">
                        <span>{total_price} ₴</span>
                        <span className={styles.delim}>|</span>
                        <span>{total_count}</span>
                        <CiShoppingCart/>
                    </NavLink>
                </div>
            </div>
        </header>)
}

export default Header;

