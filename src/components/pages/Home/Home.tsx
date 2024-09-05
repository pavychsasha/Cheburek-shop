import Categories from "../../common/Categories/Categories";
import Skeleton from "../../common/Card/Skeleton";
import Card from "../../common/Card/Card";
import React from "react";
import axios from "axios";
import styles from './Home.module.scss'
import Sort from "../../common/Sort/Sort";
import {useSelector, useDispatch} from "react-redux";
import {RootState} from '../../../redux/store'
import {setCategoryId, setSort} from "../../../redux/slices/filterSlice";

const Home = () => {
    const categoryId = useSelector((state: RootState) => state.filter.categoryId);
    const sort = useSelector((state: RootState) => state.filter.sort);
    const searchValue = useSelector((state: RootState) => state.filter.searchValue);

    const dispatch = useDispatch();

    const [items, setItems] = React.useState([]);
    const [isLoading, setIsLoading] = React.useState(false)

    const categories = ['Все', 'Чебуреки', 'Пиріжки', 'Напої', 'Інше'];

    const baseUrl = 'https://66cdd0b68ca9aa6c8ccbbb89.mockapi.io'
    const categoryParam: number | string = categoryId !== 0 ? categoryId : '';
    const sortBy = sort.sortType;
    const orderBy = sort.sortOrder;

    const onChangeCategory = (id: number) => {
        dispatch(setCategoryId(id));
    }

    const onChangeSort = (sort: object) => {
        dispatch(setSort(sort));
    }

    React.useEffect(() => {
        setIsLoading(true);
        axios.get(`${baseUrl}/items?category=${categoryParam}&sortBy=${sortBy}&order=${orderBy}&name=${searchValue}`)
            .then((res) => {
                setItems(res.data);
                setIsLoading(false);
            });
    }, [categoryId, sort, searchValue]);


    return (
        <>
            <nav>
                <Categories value={categoryId}
                            onChangeCategory={(i) => onChangeCategory(i)}
                            categories={categories}/>
                <Sort value={sort}
                      onChangeSort={(sort) => onChangeSort(sort)}/>
            </nav>
            <h2>{categories[categoryId]}</h2>
            <main className={styles.grid__wrapper}>
                {isLoading ? [...new Array(8)].map((_, index) => <Skeleton key={index}/>)
                    : items.map(food => <Card food={food}/>)}
            </main>
        </>
    )
}

export default Home;