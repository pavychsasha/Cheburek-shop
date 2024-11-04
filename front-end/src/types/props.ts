import React from "react";

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
    value: {
        nameUkr: string;
        nameEn: string;
        sortType: string;
        sortOrder: string;
    };
    onChangeSort: (sort: { nameUkr: string; sortType: string }) => void;
}

export interface ICartItemProps {
    product_id: string;
    name: string;
    image_src: string;
    count: number;
    price: number;
    isOrder?: boolean;
}