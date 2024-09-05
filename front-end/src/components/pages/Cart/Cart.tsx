import styles from './Cart.module.scss';
import { FaCartShopping } from "react-icons/fa6";
import { FaTrash } from "react-icons/fa";


const Cart = () => {
    return (
        <main className={styles.cart}>
            <div className={styles.top}>
                <div className={styles.cart__heading}>
                    <FaCartShopping />
                    <h2>Кошик</h2>
                </div>
                <div className={styles.delete}>
                    <FaTrash />
                    <span>Очистити кошик</span>
                </div>

            </div>
            <div className={styles.items}>
                nadnihdfsifbeu
            </div>
            <div className={styles.bottom}></div>
        </main>
    )
}

export default Cart;