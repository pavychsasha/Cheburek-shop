import styles from './Cart.module.scss';
import {FaCartShopping} from "react-icons/fa6";
import {FaTrash} from "react-icons/fa";
import CartItem from "../../common/CartItem/CartItem.tsx";
import {useDispatch, useSelector} from "react-redux";
import {RootState} from "../../../redux/store.ts";
import {clearCart, fetchCart} from "../../../redux/slices/cartSLice.ts";
import React from "react";


const Cart = () => {
    const isAuthorized = useSelector((state: RootState) => state.auth.isAuthorized);
    const {items, total_price, total_count} = useSelector((state: RootState) => state.cart);

    const dispatch = useDispatch();

    React.useEffect(() => {
        if (isAuthorized) {
            dispatch(fetchCart());
        }
    }, [dispatch, isAuthorized]);

    const handleClickClear = () => {
        dispatch(clearCart())
    }

    return (
        <main className={styles.cart}>
            <div className={styles.top}>
                <div className={styles.cart__heading}>
                    <FaCartShopping/>
                    <h2>Кошик</h2>
                </div>
                <div className={styles.delete} onClick={handleClickClear}>
                    <FaTrash/>
                    <span>Очистити кошик</span>
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
                    <p>Кількість товару: <span>{total_count} шт.</span></p>
                    <p>Загальна вартість: <span className={styles.total__price}>{total_price}₴</span></p>
                </div>
                <div className={styles.buttons}>

                </div>
            </div>
        </main>
    )
}

export default Cart;