import {IItem} from "./items.ts";

export interface IItemsState {
    items: IItem[];
    status: string;
    pagesCount: number;
    currentRequestId?: string;
    lastError?: string;
}

export interface ICartState {
    total_price: number;
    total_count: number;
    items: IItem[];
    fetchCartStatus: string;
    addItemStatus: string;
    subtractItemStatus: string;
    deleteItemStatus: string;
    clearCartStatus: string;
}
