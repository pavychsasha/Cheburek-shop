import React from 'react';
import styles from './Button.module.scss';

interface ButtonProps {
    label: string;
    onClick?: () => void;
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
    variant?: 'primary' | 'secondary' | 'danger';
    className?: string;
}

const Button: React.FC<ButtonProps> = ({
                                           label,
                                           onClick,
                                           type = 'button',
                                           disabled = false,
                                           variant = 'primary',
                                           className = '',
                                       }) => {
    const buttonClass = `${styles.button} ${styles[variant]} ${className}`;

    return (
        <button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={buttonClass}
        >
            {label}
        </button>
    );
};

export default Button;
