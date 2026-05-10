import styles from './Categories.module.scss';
import React from "react";
import {ICategoriesProps} from "../../../types/props.ts";

const Categories: React.FC<ICategoriesProps> = ({
    value,
    onChangeCategory,
    categories,
    categoriesEn,
    categoryMedia = {},
}) => {

    function handleOnClickCategory(index: number) {
        if (categoriesEn[index]) {
            onChangeCategory(categoriesEn[index]);
        }
    }

    return (
        <ul className={styles.list}>
            {
                categories.map((category, index) => (
                    <li key={categoriesEn[index] || category}>
                        <button
                            type="button"
                            onClick={() => handleOnClickCategory(index)}
                            className={value === categoriesEn[index] ? `${styles.item} ${styles.active}` : styles.item}
                        >
                            {categoryMedia[categoriesEn[index]] && (
                                <img src={categoryMedia[categoriesEn[index]]} alt="" />
                            )}
                            <span>{category}</span>
                        </button>
                    </li>
                ))
            }
        </ul>
    )
}

export default Categories;
