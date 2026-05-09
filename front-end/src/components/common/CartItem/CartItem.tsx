import styles from './CartItem.module.scss'
import {ImCross} from "react-icons/im";
import {
    addItemToBackend,
    deleteItemFromBackend,
    subtractItemFromBackend
} from "../../../redux/slices/cartSLice.ts";
import React from "react";
import {ICartItemProps} from "../../../types/props.ts";
import {useAppDispatch} from "../../../redux/hooks.ts";

const CartItem: React.FC<ICartItemProps> = ({product_id, name, image_src, count, price, isOrder}) => {
    const dispatch = useAppDispatch();

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
                {
                    !isOrder && <img src={image_src} alt=""/>
                }
                <h3 style={isOrder ? {fontSize: '1rem'} : undefined}>{name}</h3>
            </div>

            {!isOrder
                ?
                <>
                    <p>{price * count}₴</p>
                    <div className={styles.count} aria-label={`${name} quantity`}>
                        <button className={styles.action} type="button" onClick={handleClickMinus} aria-label={`Remove one ${name}`}>-</button>
                        <p>{count}</p>
                        <button className={styles.action} type="button" onClick={handleClickPlus} aria-label={`Add one ${name}`}>+</button>
                    </div>
                    <button className={styles.delete} type="button" onClick={handleClickDelete} aria-label={`Remove ${name} from cart`}>
                        <ImCross/>
                    </button>
                </>

                :
                <>
                    <p style={{color: '#aaa', fontSize: '1rem', margin: '0 auto 0 1rem'}}>x{count}</p>
                    <p style={{fontSize: '1rem'}}>{price * count}₴</p>
                </>

            }


        </div>
    )
}

export default CartItem;
