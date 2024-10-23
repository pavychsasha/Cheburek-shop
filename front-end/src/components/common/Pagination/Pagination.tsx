import styles from './Pagination.module.scss'
import {useSelector} from "react-redux";
import {RootState} from "../../../redux/store.ts";
import React from "react";
import {IPaginationProps} from "../../../types/props.ts";

const Pagination: React.FC<IPaginationProps> = ({setCurrentPage, currentPage}) => {

    const pagesCount = useSelector((state: RootState) => state.items.pagesCount);

    let pages = [];

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
            <ul>
                {pages.map(page =>
                    <li key={page} onClick={() => {handleChangeCurrentPage(page)}}
                        className={page == currentPage ? `${styles.page}  ${styles.active}` : styles.page}>
                        {page}
                    </li>)}
            </ul>
        </div>
    )
}

export default Pagination;