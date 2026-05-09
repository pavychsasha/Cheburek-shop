import React from "react";
import {ISortType} from "./filter.ts";

export interface IPaginationProps {
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
    currentPage: number;
}

export interface ICategoriesProps {
    value: string;
    onChangeCategory: (index: string) => void;
    categories: string[];
    categoriesEn: string[];
}

export interface ISortProps {
    value: ISortType;
    onChangeSort: (sort: ISortType) => void;
}

export interface ICartItemProps {
    product_id: string;
    name: string;
    image_src: string;
    count: number;
    price: number;
    isOrder?: boolean;
}
