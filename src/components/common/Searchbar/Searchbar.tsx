import styles from './Searchbar.module.scss';
import { CiSearch } from "react-icons/ci";
import React from "react";
import debounce from "lodash.debounce";

interface ISearchProps {
    searchValue: string;
    onChangeSearch: (value: string) => void;
}

const Searchbar: React.FC<ISearchProps> = ({ onChangeSearch }) => {
    const [localSearchValue, setLocalSearchValue] = React.useState<string>('');

    const updateSearchValue = React.useCallback(
        debounce((value: string) => {
            onChangeSearch(value);
        }, 250),
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
                placeholder={'Пошук...'}
                value={localSearchValue}
                onChange={handleChange}
            />
        </div>
    );
};

export default Searchbar;
