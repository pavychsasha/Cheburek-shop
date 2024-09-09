import styles from "./Sort.module.scss";
import React from "react";

interface ISortProps {
    value: {
        name: string;
        sortType: string;
        sortOrder: string;
    };
    onChangeSort: (sort: { name: string; sortType: string }) => void;
}

const Sort: React.FC<ISortProps> = ({value, onChangeSort}) => {
    const sortList = [
        {name: 'алфавітом(зрост.)', sortType: 'name', sortOrder: 'asc'},
        {name: 'ціною(зрост.)', sortType: 'price', sortOrder: 'asc'},
        {name: 'алфавітом(спад.)', sortType: 'name', sortOrder: 'desc'},
        {name: 'ціною(спад.)', sortType: 'price', sortOrder: 'desc'}
    ];

    const handleOnChangeSort = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const index = event.target.selectedIndex;
        onChangeSort(sortList[index]);
    };

    return (
        <div className={styles.filter}>
            <span>Сортувати за</span>
            <select value={value.sortType + value.sortOrder} onChange={handleOnChangeSort}>
                {sortList.map((sort, index) => (
                    <option key={index} value={sort.sortType + sort.sortOrder}>
                        {sort.name}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default Sort;
