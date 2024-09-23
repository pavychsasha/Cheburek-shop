import styles from '../Auth.module.scss';
import {SubmitHandler, useForm} from 'react-hook-form';
import InputField from '../../../common/InputField/InputField.tsx';
import useSubmitForm from '../../../../hooks/useSubmitForm.ts';
import {setIsAuth} from "../../../../redux/slices/authSlice.ts";
import {useDispatch, useSelector} from "react-redux";
import {RootState} from "../../../../redux/store.ts";
import {useNavigate} from 'react-router-dom'

interface IFormLogin {
    username: string;
    password: string;
}

const Login = () => {
    const {
        register,
        handleSubmit,
        setError,
        formState: {errors, isSubmitting},
    } = useForm<IFormLogin>({mode: 'onChange'});

    const navigate = useNavigate();

    const {submitForm} = useSubmitForm('http://localhost:8000/api/v1/auth/login');
    const isAuthorized = useSelector((state: RootState) => state.auth.isAuthorized);
    const dispatch = useDispatch();

    const onSubmit: SubmitHandler<IFormLogin> = async (data) => {
        const {data: responseData, error} = await submitForm({
            grant_type: '',
            username: data.username,
            password: data.password,
            scope: '',
            client_id: '',
            client_secret: '',
        });

        if (responseData) {
            dispatch(setIsAuth(true));
            navigate('/');
        } else if (error) {
            setError('password', {
                type: 'manual',
                message: error.message || 'Неправильний пароль або логін',
            });
        }
    };


    console.log(isAuthorized);

    return (
        <main className={styles.container}>
            <div className={styles.login__box}>
                <h1>Вхід</h1>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <InputField
                        label="Електронна пошта"
                        type="email"
                        placeholder="Введіть вашу електронну пошту"
                        register={register('username', {
                            required: `Це поле є обов'язковим`,
                            pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                                message: 'Некоректно введена пошта',
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
                                message: 'Некоректно введено пароль',
                            },
                        })}
                        error={errors.password}
                    />
                    <button className={styles.submit__button} type="submit" disabled={isSubmitting}>
                        {isSubmitting ? 'Виконується вхід' : 'Увійти'}
                    </button>
                </form>
                <p className={styles.forgot__password}>Забули пароль?</p>
            </div>
        </main>
    );
};

export default Login;
