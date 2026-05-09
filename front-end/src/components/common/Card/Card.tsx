import styles from './Card.module.scss'
import {FaMinus, FaPlus} from "react-icons/fa";
import {addItemToBackend, subtractItemFromBackend} from "../../../redux/slices/cartSLice.ts";
import React from "react";
import {useTranslation} from "react-i18next";
import {useAppDispatch, useAppSelector} from "../../../redux/hooks.ts";
import {useCurrencyFormatter} from "../../../hooks/useCurrencyFormatter.ts";

interface ICardProps {
    product_id: string;
    name: string;
    image_src: string;
    price: number;
}

const Card: React.FC<ICardProps> = ({product_id, name, image_src, price,}) => {
    const cartItem = useAppSelector((state) =>
        state.cart.items.find((item) => item.product_id === product_id));

    const dispatch = useAppDispatch();

    const [t] = useTranslation('global');
    const formatPrice = useCurrencyFormatter();

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
                    <p>{t('card.price')}: {formatPrice(price)}</p>
                    {itemCount === 0 ? (
                        <button className={styles.button} type="button" onClick={handleClickPlus}>
                            {t('card.button')}
                        </button>
                    ) : (
                        <div className={styles.counter} aria-label={`${name} quantity`}>
                            <button type="button" onClick={handleClickMinus} aria-label={`Remove one ${name}`}>
                                <FaMinus/>
                            </button>
                            <span>{itemCount}</span>
                            <button type="button" onClick={handleClickPlus} aria-label={`Add one ${name}`}>
                                <FaPlus/>
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default Card;
