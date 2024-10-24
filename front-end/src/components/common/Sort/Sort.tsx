import styles from "./Sort.module.scss";
import React from "react";
import {useTranslation} from "react-i18next";
import {ISortProps} from "../../../types/props.ts";

const Sort: React.FC<ISortProps> = ({value, onChangeSort}) => {
    const [t, i18n] = useTranslation('global');

    const sortList = [
        {nameUkr: 'алфавітом(зрост.)', nameEn: 'alphabet(asc)', sortType: 'name', sortOrder: 'asc'},
        {nameUkr: 'ціною(зрост.)', nameEn: 'price(asc)', sortType: 'price', sortOrder: 'asc'},
        {nameUkr: 'алфавітом(спад.)', nameEn: 'alphabet(desc)', sortType: 'name', sortOrder: 'desc'},
        {nameUkr: 'ціною(спад.)', nameEn: 'price(desc)', sortType: 'price', sortOrder: 'desc'}
    ];

    const handleOnChangeSort = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const index = event.target.selectedIndex;
        onChangeSort(sortList[index]);
    };

    return (
        <div className={styles.filter}>
            <span>{t('sort.sortBy')}</span>
            <select value={value.sortType + value.sortOrder} onChange={handleOnChangeSort}>
                {sortList.map((sort, index) => (
                    <option key={index} value={sort.sortType + sort.sortOrder}>
                        {i18n.language === 'en' ? sort.nameEn : sort.nameUkr}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default Sort;
