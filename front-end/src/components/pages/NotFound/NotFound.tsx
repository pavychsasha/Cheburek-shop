import notFoundCheburek from '../../../assets/NotFoundCheburek.png';
import styles from './NotFound.module.scss'
import {useTranslation} from "react-i18next";
const NotFound = () => {
    const [t] = useTranslation('global');

    return (
        <div className={styles.not__found}>
            <img src={notFoundCheburek} alt=""/>
            <p>{t('errorPage.errorText')}</p>

        </div>

    )
}

export default NotFound;