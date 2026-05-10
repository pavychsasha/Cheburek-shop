import Categories from "../../common/Categories/Categories";
import Skeleton from "../../common/Card/Skeleton";
import Card from "../../common/Card/Card";
import { useCallback, useEffect, useState } from "react";
import styles from './Home.module.scss';
import Sort from "../../common/Sort/Sort";
import { setCategory, setSort } from "../../../redux/slices/filterSlice";
import { fetchItems } from "../../../redux/slices/itemsSlice.ts";
import { IParams } from "../../../types/api.ts";
import Pagination from "../../common/Pagination/Pagination.tsx";
import { useTranslation } from "react-i18next";
import {ISortType} from "../../../types/filter.ts";
import {useAppDispatch, useAppSelector} from "../../../redux/hooks.ts";

const Home = () => {
    const category = useAppSelector((state) => state.filter.category);
    const sort = useAppSelector((state) => state.filter.sort);
    const searchValue = useAppSelector((state) => state.filter.searchValue);
    const { items, status, lastError } = useAppSelector((state) => state.items);
    const isLanguageSet = useAppSelector((state) => state.lang.isLanguageSet);
    const categoryMedia = useAppSelector((state) => state.settings.categoryMedia);

    const dispatch = useAppDispatch();
    const { i18n, t } = useTranslation('global');
    const queryKey = [
        category,
        searchValue,
        sort.sortType,
        sort.sortOrder,
        i18n.language,
    ].join("|");
    const [pageState, setPageState] = useState({queryKey: "", page: 1});
    const currentPage = pageState.queryKey === queryKey ? pageState.page : 1;

    const categoriesEn = ['All', 'Chebureks', 'Pies', 'Drinks', 'Other'];
    const categoriesUkr = ['Все', 'Чебуреки', 'Пиріжки', 'Напої', 'Інше'];
    const displayCategories = i18n.language === 'en' ? categoriesEn : categoriesUkr;

    const getCategoryTitle = (category: string) => {
        const language = i18n.language === 'ukr' ? 'ukr' : 'en';
        const titles: Record<'en' | 'ukr', Record<string, string>> = {
            en: { All: 'All', Chebureks: 'Chebureks', Pies: 'Pies', Drinks: 'Drinks', Other: 'Other' },
            ukr: { All: 'Все', Chebureks: 'Чебуреки', Pies: 'Пиріжки', Drinks: 'Напої', Other: 'Інше' }
        };
        return titles[language][category] || category;
    };

    const currentCategoryTitle = getCategoryTitle(category);

    const onChangeCategory = (newCategory: string) => dispatch(setCategory(newCategory));
    const onChangeSort = (sort: ISortType) => dispatch(setSort(sort));

    const getItems = useCallback(() => {
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
    }, [category, currentPage, dispatch, searchValue, sort.sortOrder, sort.sortType]);

    useEffect(() => {
        if (isLanguageSet) getItems();
    }, [getItems, isLanguageSet]);

    return (
        <>
            <section className={styles.hero}>
                <div>
                    <p>{t('home.eyebrow')}</p>
                    <h2>{t('home.title')}</h2>
                    <span>{t('home.subtitle')}</span>
                </div>
            </section>
            <nav className={styles.nav}>
                <Categories
                    value={category}
                    onChangeCategory={(newValue) => onChangeCategory(newValue)}
                    categories={displayCategories}
                    categoriesEn={categoriesEn}
                    categoryMedia={categoryMedia}
                />
            </nav>
            <div className={styles.sort}>
                <h2 className={styles.category__title}>{currentCategoryTitle}</h2>
                <Sort value={sort} onChangeSort={onChangeSort}/>
            </div>
            <main>
                <div className={styles.gridShell}>
                    {status === 'refreshing' && (
                        <div className={styles.refreshing} role="status" aria-live="polite">
                            {t('home.loading')}
                        </div>
                    )}
                    {lastError && items.length > 0 && (
                        <div className={styles.refreshError} role="status">
                            {t('home.error.text')}
                        </div>
                    )}
                    <div className={styles.grid__wrapper} aria-busy={status === 'refreshing'}>
                        {status === 'loading' && items.length === 0 && [...new Array(8)].map((_, index) => <Skeleton key={index}/>)}
                        {items.map(item => (
                            <Card
                                key={item.product_id}
                                product_id={item.product_id}
                                name={item.name}
                                image_src={item.image_src}
                                price={item.price}
                                category={item.category}
                            />
                        ))}
                        {status === 'success' && items.length === 0 && (
                            <section className={styles.empty}>
                                <h3>{t('home.empty.title')}</h3>
                                <p>{t('home.empty.text')}</p>
                            </section>
                        )}
                        {status === 'error' && items.length === 0 && (
                            <section className={styles.empty}>
                                <h3>{t('home.error.title')}</h3>
                                <p>{t('home.error.text')}</p>
                            </section>
                        )}
                    </div>
                </div>
                <Pagination
                    setCurrentPage={(page) => {
                        const nextPage = typeof page === "function" ? page(currentPage) : page;
                        setPageState({queryKey, page: nextPage});
                    }}
                    currentPage={currentPage}
                />
            </main>
        </>
    );
};

export default Home;
