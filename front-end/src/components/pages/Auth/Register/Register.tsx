import styles from '../Auth.module.scss';
import {SubmitHandler, useForm} from 'react-hook-form';
import InputField from '../../../common/InputField/InputField.tsx';
import useSubmitForm from '../../../../hooks/useSubmitForm.ts';
import {setIsAuth} from "../../../../redux/slices/authSlice.ts";
import {NavLink, useNavigate} from "react-router-dom";
import {useDispatch} from "react-redux";

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
        setError,
        formState: {errors, isSubmitting},
        getValues,
    } = useForm<IFormRegister>({mode: 'onChange'});

    const navigate = useNavigate();

    const {submitForm} = useSubmitForm('http://localhost:8000/api/v1/auth/register');
    const dispatch = useDispatch();

    const onSubmit: SubmitHandler<IFormRegister> = async (data) => {
        const {res: response, error} = await submitForm({
            email: data.email,
            password: data.password,
            username: data.username
        });

        if (response && response.status === 200) {
            dispatch(setIsAuth(true));
            navigate('/');
        } else if (error) {
            setError('rePassword', {
                type: 'manual',
                message: error.message || 'Користувач із такими даними вже існує',
            });
        }
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
                <NavLink to={'/login'}><p className={styles.forgot__password}>Вже зареєстровані?</p></NavLink>
            </div>
        </main>
    );
};

export default Register;
