import {useTranslation} from "react-i18next";
import styles from './LangSelector.module.scss';
import {RiArrowDropDownLine} from "react-icons/ri";
import React, {useRef} from "react";

const LangSelector = () => {
    const [isOpen, setIsOpen] = React.useState(false);

    const {i18n} = useTranslation();

    const dropdownRef = useRef<HTMLDivElement>(null);

    const langList = [
        {label: 'Українська', code: 'ukr'},
        {label: 'English', code: 'en'}
    ];

    const handleOnClickLang = (langCode: string) => {
        i18n.changeLanguage(langCode);
        setIsOpen(false)
    };

    React.useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <div className={styles.dropdown__menu} ref={dropdownRef}>
            <div className={styles.btn} onClick={() => {
                setIsOpen(!isOpen)
            }}>
                <p>{(i18n.language).toUpperCase()}</p>
                <RiArrowDropDownLine size={28}/>
            </div>
            <ul className={styles.list} style={{display: isOpen ? 'block' : 'none'}}>
                {langList.map(lang => (
                    <li className={styles.item}
                        key={lang.code}
                        onClick={() => handleOnClickLang(lang.code)}
                    >
                        {lang.label}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default LangSelector;
