import styles from './Categories.module.scss';
import React from "react";
import {ICategoriesProps} from "../../../types/props.ts";
import {categoryFallbackSvg} from "../../../utils/productVisuals.ts";

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
                            <span className={styles.mediaFrame} aria-hidden="true">
                                <img
                                    src={
                                        categoryMedia[categoriesEn[index]] ||
                                        categoryFallbackSvg(categoriesEn[index])
                                    }
                                    alt=""
                                />
                            </span>
                            <span>{category}</span>
                        </button>
                    </li>
                ))
            }
        </ul>
    )
}

export default Categories;
