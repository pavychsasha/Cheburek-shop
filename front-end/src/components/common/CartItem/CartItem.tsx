import styles from './CartItem.module.scss'
import {ImCross} from "react-icons/im";
import {useDispatch, useSelector} from "react-redux";
import {
    addItem,
    addItemToBackend,
    deleteItem, deleteItemFromBackend,
    removeItem,
    subtractItemFromBackend
} from "../../../redux/slices/cartSLice.ts";
import React from "react";
import {RootState} from "../../../redux/store.ts";

interface ICartItemProps {
    product_id: string;
    name: string;
    image_src: string;
    count: number;
    price: number;
}

const CartItem: React.FC<ICartItemProps> = ({product_id, name, image_src, count, price}) => {

    const isAuthorized = useSelector((state: RootState) => state.auth.isAuthorized);

    const dispatch = useDispatch();

    const handleClickPlus = () => {
        if (isAuthorized) {
            const itemToAdd = {
                product_id: product_id,
                name: name,
                image_src: image_src,
                price: price,
                count: count
            }
            dispatch(addItemToBackend(itemToAdd))
        } else {
            dispatch(addItem({
                product_id
            }))
        }
    }

    const handleClickMinus = () => {
        if (isAuthorized){
            dispatch(subtractItemFromBackend(product_id))
        } else {
            dispatch(removeItem(product_id))
        }
    }

    const handleClickDelete = () => {
        if (isAuthorized){
            dispatch(deleteItemFromBackend(product_id))
        } else {
            dispatch(deleteItem(product_id))
        }
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