import Categories from "../../common/Categories/Categories";
import Skeleton from "../../common/Card/Skeleton";
import Card from "../../common/Card/Card";
import React from "react";
import styles from './Home.module.scss';
import Sort from "../../common/Sort/Sort";
import {useSelector, useDispatch} from "react-redux";
import {RootState} from '../../../redux/store';
import {setCategory, setSort} from "../../../redux/slices/filterSlice";
import {fetchItems} from "../../../redux/slices/itemsSlice.ts";
import {IParams} from "../../../types/api.ts";


const Home = () => {

    //Getting variables from state with selectors
    const category = useSelector((state: RootState) => state.filter.category);
    const sort = useSelector((state: RootState) => state.filter.sort);
    const searchValue = useSelector((state: RootState) => state.filter.searchValue);
    const {items, status} = useSelector((state: RootState) => state.items);

    const dispatch = useDispatch();

    //List of categories
    //const categories = ['Все', 'Чебуреки', 'Пиріжки', 'Напої', 'Інше'];
    const categoriesEn = ['All', 'Chebureks', 'Pies', 'Drinks', 'Other'];

    //Handlers for setting filtration
    const onChangeCategory = (newCategory: string) => {
        dispatch(setCategory(newCategory));
    };

    const onChangeSort = (sort: object) => {
        dispatch(setSort(sort));
    };

    //Getting products with fetchItems function
    const getItems = async () => {
        const categoryParam = category !== 'All' ? category : '';
        const sortBy = sort.sortType;
        const orderBy = sort.sortOrder;

        const params: IParams = {
            categoryParam,
            sortBy,
            orderBy,
            searchValue,
        };

        //Fetching items from db using API
        dispatch(fetchItems(params));

        window.scrollTo(0, 0);
    };

    // Fetch items when category, sort, or searchValue changes
    React.useEffect(() => {
        getItems();
    }, [category, sort, searchValue]);

    return (
        <>
            <nav>
                <Categories value={category}
                            onChangeCategory={(newValue) => onChangeCategory(newValue)}
                            categories={categoriesEn}/>
            </nav>
            <div className={styles.sort}>
                <h2 className={styles.category__title}>{category}</h2>
                <Sort value={sort}
                      onChangeSort={(sort) => onChangeSort(sort)}/>
            </div>
            <main className={styles.grid__wrapper}>
                {/*Checking for loading status*/}
                {status === 'loading' ? [...new Array(8)].map((_, index) => <Skeleton key={index}/>)
                    : items.map(item =>
                        <Card
                            key={item.product_id}
                            product_id={item.product_id}
                            name={item.name}
                            image_src={item.image_src}
                            price={item.price}/>)}
            </main>
        </>
    );
};

export default Home;
