import {useTranslation} from "react-i18next";
import styles from './LangSelector.module.scss';
import {RiArrowDropDownLine} from "react-icons/ri";
import React, {useRef} from "react";
import {apiClient} from "../../../api/api.ts";

const LangSelector = () => {
    const [isOpen, setIsOpen] = React.useState(false);

    const {i18n} = useTranslation();

    const dropdownRef = useRef<HTMLDivElement>(null);

    const langList = [
        {label: 'Українська', code: 'ukr'},
        {label: 'English', code: 'en'}
    ];

    const handleOnClickLang = async (langCode: string) => {
        await apiClient.post("/languages/change_language", {}, {params: {language: langCode}});
        await apiClient.get("/languages/current_language");
        i18n.changeLanguage(langCode);
        setIsOpen(false);
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
            <button className={styles.btn} type="button" aria-haspopup="listbox" aria-expanded={isOpen} onClick={() => {
                setIsOpen(!isOpen)
            }}>
                <p>{(i18n.language).toUpperCase()}</p>
                <RiArrowDropDownLine size={28}/>
            </button>
            <ul className={styles.list} role="listbox" style={{display: isOpen ? 'block' : 'none'}}>
                {langList.map(lang => (
                    <li className={styles.item} key={lang.code}>
                        <button
                            type="button"
                            role="option"
                            aria-selected={i18n.language === lang.code}
                            onClick={() => handleOnClickLang(lang.code)}
                        >
                            {lang.label}
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default LangSelector;
