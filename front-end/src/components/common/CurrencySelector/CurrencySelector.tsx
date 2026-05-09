import {setSelectedCurrency} from "../../../redux/slices/settingsSlice.ts";
import {useAppDispatch, useAppSelector} from "../../../redux/hooks.ts";

import styles from "./CurrencySelector.module.scss";

const CurrencySelector = () => {
    const dispatch = useAppDispatch();
    const {currency, selectedCurrency} = useAppSelector((state) => state.settings);

    return (
        <label className={styles.selector}>
            <span>Currency</span>
            <select
                value={selectedCurrency}
                onChange={(event) => dispatch(setSelectedCurrency(event.target.value))}
                aria-label="Display currency"
            >
                {currency.supported_currencies.map((currencyCode) => (
                    <option key={currencyCode} value={currencyCode}>
                        {currencyCode}
                    </option>
                ))}
            </select>
        </label>
    );
};

export default CurrencySelector;
