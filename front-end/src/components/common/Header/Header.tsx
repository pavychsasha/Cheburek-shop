import cheburekLogo from "../../../assets/cheburekLogo.svg";
import {CiShoppingCart} from "react-icons/ci";
import styles from './Header.module.scss';
import Searchbar from "../Searchbar/Searchbar.tsx";
import {NavLink, useLocation} from "react-router-dom";
import {setSearchValue} from "../../../redux/slices/filterSlice.ts";
import {FaUserCircle} from "react-icons/fa";
import {useTranslation} from "react-i18next";
import LangSelector from "../LangSelector/LangSelector.tsx";
import CurrencySelector from "../CurrencySelector/CurrencySelector.tsx";
import {RiLogoutCircleRFill} from "react-icons/ri";
import {setIsAuth} from "../../../redux/slices/authSlice.ts";
import {apiClient, getAuthHeaders} from "../../../api/api.ts";
import {useAppDispatch, useAppSelector} from "../../../redux/hooks.ts";
import {useCurrencyFormatter} from "../../../hooks/useCurrencyFormatter.ts";


const Header = () => {
    const isAuthorized = useAppSelector((state) => state.auth.isAuthorized)
    const searchValue = useAppSelector((state) => state.filter.searchValue);
    const {total_price, total_count} = useAppSelector((state) => state.cart)
    const formatPrice = useCurrencyFormatter();

    const dispatch = useAppDispatch();

    const location = useLocation();

    const [t] = useTranslation('global');

    const shouldShowSearchbar = !['/cart', '/order'].includes(location.pathname);

    const onChangeSearch = (value: string) => {
        dispatch(setSearchValue(value));
    }

    const handleLogout = async () => {
        try {
            await apiClient.post("/auth/logout", {}, {headers: getAuthHeaders()});
        } finally {
            localStorage.removeItem("token");
            dispatch(setIsAuth(false));
        }
    };

    return (
        <header className={styles.header}>
            <NavLink className={styles.link} to={'/'}>
                <div className={styles.logo__and__name}>
                    <img src={cheburekLogo} className={styles.logo} alt="logo"/>
                    <div className={styles.name__and__slogan}>
                        <h1>{t("header.logo")}</h1>
                        <p>{t('header.slogan')}</p>
                    </div>
                </div>
            </NavLink>
            {shouldShowSearchbar && (
                <div className={styles.searchSlot}>
                    <Searchbar
                        searchValue={searchValue}
                        onChangeSearch={onChangeSearch}
                    />
                </div>
            )}
            <div className={styles.left}>
                <LangSelector/>
                <CurrencySelector/>
                {
                    isAuthorized
                        ?
                        <button className={styles.iconButton} type="button" onClick={handleLogout} aria-label="Log out">
                            <RiLogoutCircleRFill className={styles.user}/>
                        </button>
                        :
                        <NavLink className={styles.link} to="/register">
                            <FaUserCircle className={styles.user}/>
                        </NavLink>
                }

                <div className={styles.btn}>
                    <NavLink className={styles.link} to="/cart">
                        <span className={styles.cartPrice}>{formatPrice(total_price)}</span>
                        <span className={styles.delim}>|</span>
                        <span>{total_count}</span>
                        <CiShoppingCart/>
                    </NavLink>
                </div>
            </div>
        </header>)
}

export default Header;
