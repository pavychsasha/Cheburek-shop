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