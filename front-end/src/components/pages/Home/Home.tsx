import Categories from "../../common/Categories/Categories";
import Skeleton from "../../common/Card/Skeleton";
import Card from "../../common/Card/Card";
import React from "react";
import axios from "axios";
import styles from './Home.module.scss'
import Sort from "../../common/Sort/Sort";
import {useSelector, useDispatch} from "react-redux";
import {RootState} from '../../../redux/store'
import {setCategory, setSort} from "../../../redux/slices/filterSlice";

const Home = () => {
    const category = useSelector((state: RootState) => state.filter.category);
    const sort = useSelector((state: RootState) => state.filter.sort);
    const searchValue = useSelector((state: RootState) => state.filter.searchValue);

    const dispatch = useDispatch();

    const [items, setItems] = React.useState([]);
    const [isLoading, setIsLoading] = React.useState(false)

    const categories = ['Все', 'Чебуреки', 'Пиріжки', 'Напої', 'Інше'];

    const categoryParam = category !== 'Все' ? category : '';
    const baseUrl = 'http://localhost:8000/api/v1'
    const sortBy = sort.sortType;
    const orderBy = sort.sortOrder;

    const additionalParams = `?name=${searchValue}&category=${categoryParam}&sort_by=${sortBy}&order=${orderBy}`;

    console.log(additionalParams);

    const onChangeCategory = (newCategory: string) => {
        dispatch(setCategory(newCategory));
    }

    const onChangeSort = (sort: object) => {
        dispatch(setSort(sort));
    }

    React.useEffect(() => {
        setIsLoading(true);
        axios.get(`${baseUrl}/products/search/${additionalParams}`)
            .then((res) => {
                setItems(res.data);
                setIsLoading(false);
            });
    }, [category, sort, searchValue]);


    return (
        <>
            <nav>
                <Categories value={category}
                            onChangeCategory={(newValue) => onChangeCategory(newValue)}
                            categories={categories}/>
            </nav>
            <div className={styles.sort}>
                <h2 className={styles.category__title}>{category}</h2>
                <Sort value={sort}
                      onChangeSort={(sort) => onChangeSort(sort)}/>
            </div>
            <main className={styles.grid__wrapper}>
                {isLoading ? [...new Array(8)].map((_, index) => <Skeleton key={index}/>)
                    : items.map(food => <Card food={food}/>)}
            </main>
        </>
    )
}

export default Home;