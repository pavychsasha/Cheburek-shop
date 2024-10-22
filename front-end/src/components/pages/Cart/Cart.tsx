import styles from './Cart.module.scss';
import {FaCartShopping} from "react-icons/fa6";
import {FaTrash} from "react-icons/fa";
import CartItem from "../../common/CartItem/CartItem.tsx";
import {useDispatch, useSelector} from "react-redux";
import {RootState} from "../../../redux/store.ts";
import {clearCart, clearCartFromBackend} from "../../../redux/slices/cartSLice.ts";
import {useTranslation} from "react-i18next";

const Cart = () => {
    //Getting variables from state
    const {items, total_price, total_count} = useSelector((state: RootState) => state.cart);
    const isAuthorized = useSelector((state: RootState) => state.auth.isAuthorized)

    const dispatch = useDispatch();

    const [t] = useTranslation('global');

    //Handlers for cart actions
    const handleClickClear = () => {
        if (isAuthorized) {
            dispatch(clearCartFromBackend());
        } else {
            dispatch(clearCart());
        }
    }

    return (
        <main className={styles.cart}>
            <div className={styles.top}>
                <div className={styles.cart__heading}>
                    <FaCartShopping/>
                    <h2>{t('cart.title')}</h2>
                </div>
                <div className={styles.delete} onClick={handleClickClear}>
                    <FaTrash/>
                    <span>{t('cart.clear')}</span>
                </div>
            </div>
            <div className={styles.items}>
                {
                    items.map((item) =>
                        <CartItem key={item.product_id}
                                  product_id={item.product_id}
                                  name={item.name}
                                  price={item.price}
                                  count={item.count}
                                  image_src={item.image_src}/>)
                }
            </div>
            <div className={styles.bottom}>
                <div className={styles.detail}>
                    <p>{t('cart.totalQuantity')}: <span>{total_count} шт.</span></p>
                    <p>{t('cart.totalPrice')}: <span className={styles.total__price}>{total_price}₴</span></p>
                </div>
                <div className={styles.buttons}>

                </div>
            </div>
        </main>
    )
}

export default Cart;