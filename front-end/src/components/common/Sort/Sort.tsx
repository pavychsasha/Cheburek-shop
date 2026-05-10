import styles from "./Sort.module.scss";
import React from "react";
import {useTranslation} from "react-i18next";
import {ISortProps} from "../../../types/props.ts";

const Sort: React.FC<ISortProps> = ({value, onChangeSort}) => {
    const [t, i18n] = useTranslation('global');
    const [isOpen, setIsOpen] = React.useState(false);
    const menuRef = React.useRef<HTMLDivElement | null>(null);

    const sortList = [
        {nameUkr: 'алфавітом(зрост.)', nameEn: 'alphabet(asc)', sortType: 'name', sortOrder: 'asc'},
        {nameUkr: 'ціною(зрост.)', nameEn: 'price(asc)', sortType: 'price', sortOrder: 'asc'},
        {nameUkr: 'алфавітом(спад.)', nameEn: 'alphabet(desc)', sortType: 'name', sortOrder: 'desc'},
        {nameUkr: 'ціною(спад.)', nameEn: 'price(desc)', sortType: 'price', sortOrder: 'desc'}
    ];

    const selectedSort = sortList.find(
        (sort) => sort.sortType === value.sortType && sort.sortOrder === value.sortOrder,
    ) || sortList[0];
    const selectedLabel = i18n.language === 'en' ? selectedSort.nameEn : selectedSort.nameUkr;

    React.useEffect(() => {
        const handlePointerDown = (event: PointerEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("pointerdown", handlePointerDown);
        return () => document.removeEventListener("pointerdown", handlePointerDown);
    }, []);

    return (
        <div className={styles.filter} ref={menuRef}>
            <span>{t('sort.sortBy')}</span>
            <div className={styles.menu}>
                <button
                    type="button"
                    className={styles.trigger}
                    aria-haspopup="listbox"
                    aria-expanded={isOpen}
                    onClick={() => setIsOpen((open) => !open)}
                >
                    {selectedLabel}
                </button>
                {isOpen && (
                    <div className={styles.options} role="listbox" aria-label={t('sort.sortBy')}>
                        {sortList.map((sort) => {
                            const label = i18n.language === 'en' ? sort.nameEn : sort.nameUkr;
                            const isSelected =
                                sort.sortType === value.sortType &&
                                sort.sortOrder === value.sortOrder;
                            return (
                                <button
                                    key={`${sort.sortType}-${sort.sortOrder}`}
                                    type="button"
                                    role="option"
                                    aria-selected={isSelected}
                                    className={isSelected ? styles.selectedOption : styles.option}
                                    onClick={() => {
                                        onChangeSort(sort);
                                        setIsOpen(false);
                                    }}
                                >
                                    {label}
                                </button>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Sort;
