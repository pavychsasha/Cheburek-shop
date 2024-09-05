import notFoundCheburek from '../../../assets/NotFoundCheburek.png';
import styles from './NotFound.module.scss'
const NotFound = () => {
    return (
        <div className={styles.not__found}>
            <img src={notFoundCheburek} alt=""/>
            <p>Сторінку не знайдено</p>

        </div>

    )
}

export default NotFound;