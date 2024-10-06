import {useEffect} from 'react';
import styles from '../Auth.module.scss';
import {SubmitHandler, useForm} from 'react-hook-form';
import InputField from '../../../common/InputField/InputField.tsx';
import useSubmitForm from '../../../../hooks/useSubmitForm.ts';
import {setIsAuth} from "../../../../redux/slices/authSlice.ts";
import {useDispatch} from "react-redux";
import {useNavigate} from 'react-router-dom';
import axios from 'axios';

//Type type(interface) of login form
interface IFormLogin {
    username: string;
    password: string;
}

const Login = () => {

    //Parameters for login form
    const {
        register,
        handleSubmit,
        setError,
        formState: {errors, isSubmitting},
    } = useForm<IFormLogin>({mode: 'onChange'});

    const navigate = useNavigate();

    const {submitForm} = useSubmitForm('http://localhost:8000/api/v1/auth/login');

/*
    const bearerToken = useSelector((state: RootState) => state.auth.bearerToken)
*/

    const dispatch = useDispatch();

    const onSubmit: SubmitHandler<IFormLogin> = async (data) => {
        const {res: response, error} = await submitForm({

            //User data for login
            grant_type: '',
            username: data.username,
            password: data.password,
            scope: '',
            client_id: '',
            client_secret: '',
        });

        //Checking for response auth/login
        if (response && response.status === 204) {
            dispatch(setIsAuth(true));
            navigate('/');
        } else if (error) {
            setError('password', {
                type: 'manual',
                message: error.message || 'Неправильний пароль або логін',
            });
        }
    };

    useEffect(() => {

        //Checking for login status /users/me
        axios.get('http://localhost:8000/api/v1/users/me', {
            withCredentials: true
        }).then(res => {
            if (res.data) {
                dispatch(setIsAuth(true));
                navigate('/');
            }
        })
    }, [dispatch, navigate]);

    return (
        <main className={styles.container}>
            <div className={styles.login__box}>
                <h1>Вхід</h1>
                <form onSubmit={handleSubmit(onSubmit)}>

                    {/*Email field*/}
                    <InputField
                        label="Електронна пошта"
                        type="text"
                        placeholder="Введіть ваше ім'я користувача"
                        register={register('username', {
                            required: `Це поле є обов'язковим`,
                            pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                                message: `Некоректно введенне ім'я користувача`,
                            },
                        })}
                        error={errors.username}
                    />

                    {/*Password field*/}
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
