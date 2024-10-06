import styles from './CartItem.module.scss'
import {ImCross} from "react-icons/im";
import {useDispatch, useSelector} from "react-redux";
import {addItem, addItemToBackend, deleteItem, removeItem} from "../../../redux/slices/cartSLice.ts";
import React from "react";
import {RootState} from "../../../redux/store.ts";

interface ICartItemProps {
    id: string;
    name: string;
    imageSrc: string;
    count: number;
    price: number;
}

const CartItem: React.FC<ICartItemProps> = ({id, name, imageSrc, count, price}) => {

    const isAuthorized = useSelector((state: RootState) => state.auth.isAuthorized);

    const dispatch = useDispatch();

    const handleClickPlus = () => {
        if (isAuthorized){
            const itemsToAdd = {
                product_id: id,
                count: 1
            }
            dispatch(addItemToBackend(itemsToAdd))
        } else {
            dispatch(addItem({
                id
            }))
        }
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