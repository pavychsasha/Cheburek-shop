import {useCallback} from "react";

import {useAppSelector} from "../redux/hooks.ts";
import {formatCurrency} from "../utils/currency.ts";

export const useCurrencyFormatter = () => {
    const {currency, selectedCurrency} = useAppSelector((state) => state.settings);

    return useCallback(
        (amount: number) => formatCurrency(amount, currency, selectedCurrency),
        [currency, selectedCurrency],
    );
};
