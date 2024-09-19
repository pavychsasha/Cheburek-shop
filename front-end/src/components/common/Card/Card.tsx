import styles from './Card.module.scss'
import {FaMinus, FaPlus} from "react-icons/fa";
import {addItem, removeItem} from "../../../redux/slices/cartSLice.ts";
import {useDispatch, useSelector} from "react-redux";
import {RootState} from "../../../redux/store.ts";

const Card = (props: any) => {
    const cartItem = useSelector((state: RootState) =>
        state.cart.items.find((item) => item.id === props.food.product_id))

    const dispatch = useDispatch();

    const itemCount = cartItem ? cartItem.count : 0;

    function handleClickPlus() {
        console.log("Clicked add");
        const newItem = {
            id: props.food.product_id,
            imageUrl: props.food.image_src,
            name: props.food.name,
            price: props.food.price,
            count: 0
        }
        dispatch(addItem(newItem));
    }

    function handleClickMinus() {
        dispatch(removeItem(props.food.product_id));
    }

    return (
        <div className={styles.wrapper}>
            <div className={styles.card}>
                <img src={props.food.image_src}
                     alt="Чебурек"/>
                <h3>{props.food.name}</h3>
                <div className={styles.bottom}>
                    <p>ціна: {props.food.price}₴</p>
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