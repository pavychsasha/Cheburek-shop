import styles from './Card.module.scss'
//import cheburek from '../../../assets/cheburek.png'
import {FaMinus, FaPlus} from "react-icons/fa";
import {useState} from "react";


let Card = (props: any) => {
    const [countOfGood, setCountOfGood] = useState(0)

    function handleClickPlus() {
        setCountOfGood(countOfGood + 1);
    }

    function handleClickMinus() {
        setCountOfGood(countOfGood - 1);
    }

    console.log(props.food.imageUrl);

    return (
        <div className={styles.wrapper}>
            <div className={styles.card}>
                <img src={props.food.image_src}
                     alt="Чебурек"/>
                <h3>{props.food.name}</h3>
                <div className={styles.bottom}>
                    <p>ціна: {props.food.price}</p>
                    <div className={styles.button} onClick={countOfGood === 0 ? handleClickPlus : undefined}>
                        {countOfGood !== 0 && <FaMinus onClick={handleClickMinus}/>}
                        <p>{countOfGood === 0 ? 'Добавити' : <span>{countOfGood}</span>}</p>
                        <FaPlus onClick={handleClickPlus}/>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Card;