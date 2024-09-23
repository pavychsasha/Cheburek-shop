interface ISortType {
    name: string;
    sortType: string;
    sortOrder: string;
}

export interface IFilterState {
    category: string;
    sort: ISortType;
    searchValue: string;
}