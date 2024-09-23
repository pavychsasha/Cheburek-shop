import styles from './Card.module.scss'
import {FaMinus, FaPlus} from "react-icons/fa";
import {addItem, removeItem} from "../../../redux/slices/cartSLice.ts";
import {useDispatch, useSelector} from "react-redux";
import {RootState} from "../../../redux/store.ts";
import React from "react";

interface ICardProps {
    id: number;
    name: string;
    imageSrc: string;
    price: number;
}

const Card: React.FC<ICardProps> = ({id, name, imageSrc, price, }) => {
    const cartItem = useSelector((state: RootState) =>
        state.cart.items.find((item) => item.id === id))

    const dispatch = useDispatch();

    const itemCount = cartItem ? cartItem.count : 0;

    const handleClickPlus = React.useCallback(() => {
        const newItem = {
            id: id,
            imageSrc: imageSrc,
            name: name,
            price: price,
            count: 0
        }
        dispatch(addItem(newItem));
    }, [dispatch, id, imageSrc, name, price]);

    const handleClickMinus = React.useCallback(() => {
        dispatch(removeItem(id));
    }, [dispatch, id]);


    return (
        <div className={styles.wrapper}>
            <div className={styles.card}>
                <img src={imageSrc}
                     alt="Чебурек"/>
                <h3>{name}</h3>
                <div className={styles.bottom}>
                    <p>ціна: {price}₴</p>
                    <div className={styles.button} onClick={itemCount === 0 ? handleClickPlus : undefined}>
                        {itemCount !== 0 && <FaMinus onClick={handleClickMinus}/>}
                        <p>{itemCount === 0 ? 'Добавити' : <span>{itemCount}</span>}</p>
                        {itemCount !== 0 && <FaPlus onClick={handleClickPlus}/>}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Card;