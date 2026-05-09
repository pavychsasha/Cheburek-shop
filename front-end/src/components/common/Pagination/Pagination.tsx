import styles from './Pagination.module.scss'
import React from "react";
import {IPaginationProps} from "../../../types/props.ts";
import {useAppSelector} from "../../../redux/hooks.ts";

const Pagination: React.FC<IPaginationProps> = ({setCurrentPage, currentPage}) => {

    const pagesCount = useAppSelector((state) => state.items.pagesCount);

    const pages = [];

    for (let i = 1; i <= pagesCount; i++) {
        pages.push(i);
    }

    const handleChangeCurrentPage = (page: number) => {
        if (currentPage !== page) {
            setCurrentPage(page)
        }
    }

    return (
        <div className={styles.pagination}>
            <ul className={styles.list}>
                {pages.map(page =>
                    <li key={page}>
                        <button type="button" onClick={() => {handleChangeCurrentPage(page)}}
                        className={page == currentPage ? `${styles.page}  ${styles.active}` : styles.page}>
                        {page}
                        </button>
                    </li>)}
            </ul>
        </div>
    )
}

export default Pagination;
