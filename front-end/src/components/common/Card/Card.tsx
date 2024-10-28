import styles from './Card.module.scss'
import {FaMinus, FaPlus} from "react-icons/fa";
import {addItemToBackend, subtractItemFromBackend} from "../../../redux/slices/cartSLice.ts";
import {useDispatch, useSelector} from "react-redux";
import {RootState} from "../../../redux/store.ts";
import React from "react";
import {useTranslation} from "react-i18next";

interface ICardProps {
    product_id: string;
    name: string;
    image_src: string;
    price: number;
}

const Card: React.FC<ICardProps> = ({product_id, name, image_src, price,}) => {
    const cartItem = useSelector((state: RootState) =>
        state.cart.items.find((item) => item.product_id === product_id));

    const dispatch = useDispatch();

    const [t] = useTranslation('global');

    const itemCount = cartItem ? cartItem.count : 0;

    const handleClickPlus = React.useCallback(() => {
        const newItem = {
            product_id: product_id,
            image_src: image_src,
            name: name,
            price: price,
            count: 0
        }
        dispatch(addItemToBackend(newItem));
    }, [dispatch, product_id, image_src, name, price]);

    const handleClickMinus = React.useCallback(() => {
        dispatch(subtractItemFromBackend(product_id));
    }, [dispatch, product_id]);

    return (
        <div className={styles.wrapper}>
            <div className={styles.card}>
                <img src={image_src}
                     alt={name}/>
                <h3>{name}</h3>
                <div className={styles.bottom}>
                    <p>{t('card.price')}: {price}₴</p>
                    <div className={styles.button} onClick={itemCount === 0 ? handleClickPlus : undefined}>
                        {itemCount !== 0 && <FaMinus onClick={handleClickMinus}/>}
                        <p>{itemCount === 0 ? t('card.button') : <span>{itemCount}</span>}</p>
                        {itemCount !== 0 && <FaPlus onClick={handleClickPlus}/>}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Card;