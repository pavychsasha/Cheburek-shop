import styles from '../Auth.module.scss';
import {SubmitHandler, useForm} from 'react-hook-form';
import InputField from '../../../common/InputField/InputField.tsx';
import useSubmitForm from '../../../../hooks/useSubmitForm.ts';

interface IFormRegister {
    email: string;
    password: string;
    rePassword: string;
    username: string;
}

const Register = () => {
    const {
        register,
        handleSubmit,
        formState: {errors, isSubmitting},
        getValues,
    } = useForm<IFormRegister>({mode: 'onChange'});

    const {submitForm} = useSubmitForm('http://localhost:8000/api/v1/auth/register');

    const onSubmit: SubmitHandler<IFormRegister> = async (data) => {
        await submitForm({
            email: data.email,
            password: data.password,
            username: data.username
        });
    };

    return (
        <main className={styles.container}>
            <div className={styles.login__box}>
                <h1>Реєстрація</h1>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <InputField
                        label="Електронна пошта"
                        type="email"
                        placeholder="Введіть вашу електронну пошту"
                        register={register('email', {
                            required: `Це поле є обов'язковим`,
                            pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                                message: 'Некоректно введена пошта',
                            },
                        })}
                        error={errors.email}
                    />
                    <InputField
                        label="Ім'я користувача"
                        type="text"
                        placeholder="Введіть ваше ім`я користувача"
                        register={register('username', {
                            required: `Це поле є обов'язковим`,
                            pattern: {
                                value: /^[A-Z0-9._%+-]{3,16}$/i,
                                message: 'Некоректно введене ім`я користувача',
                            },
                        })}
                        error={errors.username}
                    />
                    <InputField
                        label="Пароль"
                        type="password"
                        placeholder="Введіть ваш пароль"
                        register={register('password', {
                            required: `Це поле є обов'язковим`,
                            pattern: {
                                value: /^[A-Za-z\d@$!%*?&]{8,16}$/,
                                message: 'Пароль повинен містити від 8 до 16 символів',
                            },
                        })}
                        error={errors.password}
                    />
                    <InputField
                        label="Повторіть пароль"
                        type="password"
                        placeholder="Введіть ваш пароль повторно"
                        register={register('rePassword', {
                            required: `Це поле є обов'язковим`,
                            validate: (value) => value === getValues('password') || 'Паролі повинні збігатися',
                        })}
                        error={errors.rePassword}
                    />
                    <button className={styles.submit__button} type="submit" disabled={isSubmitting}>
                        {isSubmitting ? 'Виконується реєстрація' : 'Зареєструватися'}
                    </button>
                </form>
                <p className={styles.forgot__password}>Вже зареєстровані?</p>
            </div>
        </main>
    );
};

export default Register;
