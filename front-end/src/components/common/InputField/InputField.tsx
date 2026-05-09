import React from 'react';
import { FieldError, UseFormRegisterReturn } from 'react-hook-form';
import styles from './InputField.module.scss';

interface InputFieldProps {
    label: string;
    type: string;
    placeholder: string;
    register: UseFormRegisterReturn;
    error?: FieldError
}

const InputField: React.FC<InputFieldProps> = ({ label, type, placeholder, register, error }) => {
    return (
        <div className={styles.input__field}>
            <label>{label}<span>*</span></label>
            <input
                type={type}
                placeholder={placeholder}
                {...register}
            />
            {error && <p className={styles.error}>{error.message}</p>}
        </div>
    );
};

export default InputField;
