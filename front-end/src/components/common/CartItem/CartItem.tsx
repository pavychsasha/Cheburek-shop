import styles from './CartItem.module.scss'
import {ImCross} from "react-icons/im";
import {useDispatch} from "react-redux";
import {addItem, deleteItem, removeItem} from "../../../redux/slices/cartSLice.ts";
import React from "react";

interface ICartItemProps {
    id: number;
    name: string;
    imageSrc: string;
    count: number;
    price: number;
}

const CartItem: React.FC<ICartItemProps> = ({id, name, imageSrc, count, price}) => {

    const dispatch = useDispatch();

    const handleClickPlus = () => {
        dispatch(addItem({
            id
        }))
    }

    const handleClickMinus = () => {
        dispatch(removeItem(id))
    }


    const handleClickDelete = () => {
        dispatch(deleteItem(id))
    }

    return (
        <div className={styles.cart__item}>
            <div className={styles.info}>
                <img src={imageSrc} alt=""/>
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