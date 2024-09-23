import {IItem} from "./items.ts";

export interface IItemsState {
    items: IItem[];
    status: string;
}