import styles from './Categories.module.scss';
import React from "react";

interface ICategoriesProps {
    value: string;
    onChangeCategory: (index: string) => void;
    categories: string[];
}

const Categories: React.FC<ICategoriesProps> = ({value, onChangeCategory, categories}) => {

    function handleOnClickCategory(newValue: string) {
        onChangeCategory(newValue);
    }

    return (
        <ul>
            {
                categories.map((category, index) => (
                    <li
                        key={index}
                        onClick={() => handleOnClickCategory(categories[index])}
                        className={value === categories[index] ? `${styles.item} ${styles.active}` : styles.item}
                    >
                        {category}
                    </li>
                ))
            }
        </ul>
    )
}

export default Categories;
