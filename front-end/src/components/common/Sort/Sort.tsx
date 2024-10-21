import styles from "./Sort.module.scss";
import React from "react";
import {useTranslation} from "react-i18next";

interface ISortProps {
    value: {
        nameUa: string;
        nameEn: string;
        sortType: string;
        sortOrder: string;
    };
    onChangeSort: (sort: { nameUa: string; sortType: string }) => void;
}

const Sort: React.FC<ISortProps> = ({value, onChangeSort}) => {
    const [t] = useTranslation('global');

    const sortList = [
        {nameUa: 'алфавітом(зрост.)', nameEn: 'alphabet(asc)', sortType: 'name', sortOrder: 'asc'},
        {nameUa: 'ціною(зрост.)', nameEn: 'price(asc)', sortType: 'price', sortOrder: 'asc'},
        {nameUa: 'алфавітом(спад.)', nameEn: 'alphabet(desc)', sortType: 'name', sortOrder: 'desc'},
        {nameUa: 'ціною(спад.)', nameEn: 'price(desc)', sortType: 'price', sortOrder: 'desc'}
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
                        {sort.nameUa}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default Sort;
