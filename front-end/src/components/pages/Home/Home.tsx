import Categories from "../../common/Categories/Categories";
import Skeleton from "../../common/Card/Skeleton";
import Card from "../../common/Card/Card";
import React, { useEffect, useRef, useState } from "react";
import styles from './Home.module.scss';
import Sort from "../../common/Sort/Sort";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from '../../../redux/store';
import { setCategory, setSort } from "../../../redux/slices/filterSlice";
import { fetchItems } from "../../../redux/slices/itemsSlice.ts";
import { IParams } from "../../../types/api.ts";
import Pagination from "../../common/Pagination/Pagination.tsx";
import { useTranslation } from "react-i18next";

const Home = () => {
    const category = useSelector((state: RootState) => state.filter.category);
    const sort = useSelector((state: RootState) => state.filter.sort);
    const searchValue = useSelector((state: RootState) => state.filter.searchValue);
    const { items, status } = useSelector((state: RootState) => state.items);
    const isLanguageSet = useSelector((state: RootState) => state.lang.isLanguageSet);

    const dispatch = useDispatch();
    const { i18n } = useTranslation();
    const [currentPage, setCurrentPage] = useState(1);

    const categoriesEn = ['All', 'Chebureks', 'Pies', 'Drinks', 'Other'];
    const categoriesUkr = ['Все', 'Чебуреки', 'Пиріжки', 'Напої', 'Інше'];
    const displayCategories = i18n.language === 'en' ? categoriesEn : categoriesUkr;

    const getCategoryTitle = (category: string) => {
        const titles = {
            en: { All: 'All', Chebureks: 'Chebureks', Pies: 'Pies', Drinks: 'Drinks', Other: 'Other' },
            ukr: { All: 'Все', Chebureks: 'Чебуреки', Pies: 'Пиріжки', Drinks: 'Напої', Other: 'Інше' }
        };
        return titles[i18n.language]?.[category] || category;
    };

    const currentCategoryTitle = getCategoryTitle(category);

    const onChangeCategory = (newCategory: string) => dispatch(setCategory(newCategory));
    const onChangeSort = (sort: object) => dispatch(setSort(sort));

    const getItems = () => {
        const categoryParam = category !== 'All' ? category : '';
        const sortBy = sort.sortType;
        const orderBy = sort.sortOrder;

        const params: IParams = {
            categoryParam,
            sortBy,
            orderBy,
            searchValue,
            currentPage,
        };

        dispatch(fetchItems(params));
        window.scrollTo(0, 0);
    };

    useEffect(() => {
        if (isLanguageSet) getItems();
    }, [i18n.language, category, sort, searchValue, currentPage, isLanguageSet]);

    return (
        <>
            <nav>
                <Categories
                    value={category}
                    onChangeCategory={(newValue) => onChangeCategory(newValue)}
                    categories={displayCategories}
                    categoriesEn={categoriesEn}
                />
            </nav>
            <div className={styles.sort}>
                <h2 className={styles.category__title}>{currentCategoryTitle}</h2>
                <Sort value={sort} onChangeSort={onChangeSort}/>
            </div>
            <main>
                <div className={styles.grid__wrapper}>
                    {status === 'loading'
                        ? [...new Array(8)].map((_, index) => <Skeleton key={index}/>)
                        : items.map(item => (
                            <Card
                                key={item.product_id}
                                product_id={item.product_id}
                                name={item.name}
                                image_src={item.image_src}
                                price={item.price}
                            />
                        ))
                    }
                </div>
                <Pagination setCurrentPage={setCurrentPage} currentPage={currentPage}/>
            </main>
        </>
    );
};

export default Home;
