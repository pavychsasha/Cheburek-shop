import styles from './Categories.module.scss';
import React from "react";
import {ICategoriesProps} from "../../../types/props.ts";

const Categories: React.FC<ICategoriesProps> = ({value, onChangeCategory, categories, categoriesEn}) => {

    function handleOnClickCategory(index: number) {
        if (categoriesEn[index]) {
            onChangeCategory(categoriesEn[index]);
        }
    }

    return (
        <ul>
            {
                categories.map((category, index) => (
                    <li
                        key={index}
                        onClick={() => handleOnClickCategory(index)}
                        className={value === categoriesEn[index] ? `${styles.item} ${styles.active}` : styles.item}
                    >
                        {category}
                    </li>
                ))
            }
        </ul>
    )
}

export default Categories;
