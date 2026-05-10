import styles from './Cart.module.scss';
import {FaCartShopping} from "react-icons/fa6";
import {FaTrash} from "react-icons/fa";
import CartItem from "../../common/CartItem/CartItem.tsx";
import {clearCartFromBackend} from "../../../redux/slices/cartSLice.ts";
import {useTranslation} from "react-i18next";
import Button from "../../common/Button/Button.tsx";
import {useNavigate} from "react-router-dom";
import {useAppDispatch, useAppSelector} from "../../../redux/hooks.ts";
import {useCurrencyFormatter} from "../../../hooks/useCurrencyFormatter.ts";
import SimilarItems from "../../common/SimilarItems/SimilarItems.tsx";

const Cart = () => {
    //Getting variables from state
    const {items, total_price, total_count} = useAppSelector((state) => state.cart);

    const dispatch = useAppDispatch();

    const navigate = useNavigate();

    const [t] = useTranslation('global');
    const formatPrice = useCurrencyFormatter();

    //Handlers for cart actions
    const handleClickClear = () => {
        dispatch(clearCartFromBackend());
    }

    return (
        <main className={styles.cart}>
            <div className={styles.top}>
                <div className={styles.cart__heading}>
                    <FaCartShopping/>
                    <h2>{t('cart.title')}</h2>
                </div>
                <button className={styles.delete} type="button" onClick={handleClickClear} disabled={total_count === 0}>
                    <FaTrash/>
                    <span>{t('cart.clear')}</span>
                </button>
            </div>
            {items.length > 0 ? (
                <div className={styles.items}>
                    {items.map((item) =>
                        <CartItem key={item.product_id}
                                  product_id={item.product_id}
                                  name={item.name}
                                  price={item.price}
                                  count={item.count}
                                  image_src={item.image_src}/>)}
                </div>
            ) : (
                <div className={styles.empty}>
                    <h3>{t('cart.empty.title')}</h3>
                    <p>{t('cart.empty.text')}</p>
                </div>
            )}
            <div className={styles.bottom}>
                <div className={styles.detail}>
                    <p>{t('cart.totalQuantity')}: <span>{total_count}</span></p>
                    <p>{t('cart.totalPrice')}: <span className={styles.total__price}>{formatPrice(total_price)}</span></p>
                </div>
                <div className={styles.buttons}>
                    <Button
                        label={t('cart.back')}
                        type="button"
                        variant="secondary"
                        onClick={() => navigate('/')}
                    />
                    <Button
                        label={t('cart.checkout')}
                        type="button"
                        variant="primary"
                        disabled={total_count === 0}
                        onClick={() => navigate('/order')}
                    />
                </div>
            </div>
            <SimilarItems productIds={items.map((item) => item.product_id)} />
        </main>
    )
}

export default Cart;
