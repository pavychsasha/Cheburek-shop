import {useEffect, useState} from "react";
import {useTranslation} from "react-i18next";

import {fetchSimilarProducts} from "../../../api/api.ts";
import type {IItem} from "../../../types/items.ts";
import Card from "../Card/Card.tsx";
import styles from "./SimilarItems.module.scss";

interface SimilarItemsProps {
    productIds: string[];
}

const SimilarItems = ({productIds}: SimilarItemsProps) => {
    const [items, setItems] = useState<IItem[]>([]);
    const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
    const [loadedKey, setLoadedKey] = useState("");
    const [t] = useTranslation("global");
    const productIdsKey = productIds.filter(Boolean).join("|");

    useEffect(() => {
        const uniqueProductIds = Array.from(
            new Set(productIdsKey ? productIdsKey.split("|") : []),
        );
        if (uniqueProductIds.length === 0) {
            return;
        }

        let isMounted = true;
        fetchSimilarProducts(uniqueProductIds, 4)
            .then((nextItems) => {
                if (!isMounted) {
                    return;
                }
                setItems(nextItems);
                setLoadedKey(productIdsKey);
                setStatus("success");
            })
            .catch(() => {
                if (isMounted) {
                    setStatus("error");
                }
            });

        return () => {
            isMounted = false;
        };
    }, [productIdsKey]);

    if (
        !productIdsKey ||
        loadedKey !== productIdsKey ||
        status === "idle" ||
        status === "error" ||
        items.length === 0
    ) {
        return null;
    }

    return (
        <section className={styles.shelf}>
            <div className={styles.heading}>
                <p>{t("similar.eyebrow")}</p>
                <h2>{t("similar.title")}</h2>
            </div>
            <div className={styles.grid}>
                {items.map((item) => (
                    <Card
                        key={item.product_id}
                        product_id={item.product_id}
                        name={item.name}
                        image_src={item.image_src}
                        price={item.price}
                    />
                ))}
            </div>
        </section>
    );
};

export default SimilarItems;
