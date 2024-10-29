import styles from './CartItem.module.scss'
import {ImCross} from "react-icons/im";
import {useDispatch} from "react-redux";
import {
    addItemToBackend,
    deleteItemFromBackend,
    subtractItemFromBackend
} from "../../../redux/slices/cartSLice.ts";
import React from "react";
import {ICartItemProps} from "../../../types/props.ts";

const CartItem: React.FC<ICartItemProps> = ({product_id, name, image_src, count, price}) => {
    const dispatch = useDispatch();

    const handleClickPlus = () => {
        const itemToAdd = {
            product_id: product_id,
            name: name,
            image_src: image_src,
            price: price,
            count: count
        }
        dispatch(addItemToBackend(itemToAdd))
    }

    const handleClickMinus = () => {
        dispatch(subtractItemFromBackend(product_id))
    }

    const handleClickDelete = () => {
        dispatch(deleteItemFromBackend(product_id))
    }

    return (
        <div className={styles.cart__item}>
            <div className={styles.info}>
                <img src={image_src} alt=""/>
                <h3>{name}</h3>
            </div>
            <p>{price * count}₴</p>
            <div className={styles.count}>
                <span className={styles.action} onClick={handleClickMinus}>-</span>
                <p>{count}</p>
                <span className={styles.action} onClick={handleClickPlus}>+</span>
            </div>
            <ImCross onClick={handleClickDelete}/>
        </div>
    )
}

export default CartItem;