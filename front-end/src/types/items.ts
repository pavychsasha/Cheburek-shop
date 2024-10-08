export interface IItem {
    product_id: string;
    name: string;
    price: number;
    description?: string;
    category?: string;
    stock_quantity?: number;
    image_src: string;
}