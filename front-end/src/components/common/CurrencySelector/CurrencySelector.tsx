import {useEffect, useRef, useState} from "react";

import {setSelectedCurrency} from "../../../redux/slices/settingsSlice.ts";
import {useAppDispatch, useAppSelector} from "../../../redux/hooks.ts";

import styles from "./CurrencySelector.module.scss";

const CurrencySelector = () => {
    const dispatch = useAppDispatch();
    const {currency, selectedCurrency} = useAppSelector((state) => state.settings);
    const [isOpen, setIsOpen] = useState(false);
    const rootRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        const handlePointerDown = (event: PointerEvent) => {
            if (!rootRef.current?.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("pointerdown", handlePointerDown);
        return () => document.removeEventListener("pointerdown", handlePointerDown);
    }, []);

    const selectCurrency = (currencyCode: string) => {
        dispatch(setSelectedCurrency(currencyCode));
        setIsOpen(false);
    };

    return (
        <div className={styles.selector} ref={rootRef}>
            <button
                type="button"
                className={styles.trigger}
                aria-label="Display currency"
                aria-haspopup="listbox"
                aria-expanded={isOpen}
                onClick={() => setIsOpen((open) => !open)}
            >
                {selectedCurrency}
            </button>
            {isOpen && (
                <div className={styles.menu} role="listbox">
                    {currency.supported_currencies.map((currencyCode) => (
                        <button
                            key={currencyCode}
                            type="button"
                            role="option"
                            aria-selected={currencyCode === selectedCurrency}
                            className={currencyCode === selectedCurrency ? styles.optionActive : styles.option}
                            onClick={() => selectCurrency(currencyCode)}
                        >
                            {currencyCode}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CurrencySelector;
