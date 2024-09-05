import styles from './Categories.module.scss';
import React from "react";

interface ICategoriesProps {
    value: number;
    onChangeCategory: (index: number) => void;
    categories: string[];
}

const Categories: React.FC<ICategoriesProps> = ({value, onChangeCategory, categories}) => {

    function handleOnClickCategory(index: number) {
        onChangeCategory(index);
    }

    return (
        <ul>
            {
                categories.map((category, index) => (
                    <li
                        key={index}
                        onClick={() => handleOnClickCategory(index)}
                        className={value === index ? styles.active : ''}
                    >
                        {category}
                    </li>
                ))
            }
        </ul>
    )
}

export default Categories;
