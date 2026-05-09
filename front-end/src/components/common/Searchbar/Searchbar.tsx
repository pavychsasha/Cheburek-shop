import styles from './Searchbar.module.scss';
import { CiSearch } from "react-icons/ci";
import React from "react";
import debounce from "lodash.debounce";
import {useTranslation} from "react-i18next";

interface ISearchProps {
    searchValue: string;
    onChangeSearch: (value: string) => void;
}

const Searchbar: React.FC<ISearchProps> = ({ onChangeSearch }) => {
    const [localSearchValue, setLocalSearchValue] = React.useState<string>('');

    const [t] = useTranslation('global');

    const updateSearchValue = React.useMemo(
        () => debounce((value: string) => {
            onChangeSearch(value);
        }, 350),
        [onChangeSearch]
    );

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setLocalSearchValue(event.target.value);
        updateSearchValue(event.target.value);
    };

    React.useEffect(() => {
        return () => {
            updateSearchValue.cancel();
        };
    }, [updateSearchValue]);

    return (
        <div className={styles.container}>
            <CiSearch />
            <input
                type="text"
                placeholder={t('searchbar.placeholder')}
                value={localSearchValue}
                onChange={handleChange}
            />
        </div>
    );
};

export default Searchbar;
