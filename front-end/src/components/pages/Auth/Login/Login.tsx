import styles from '../Auth.module.scss';
import {SubmitHandler, useForm} from 'react-hook-form';
import InputField from '../../../common/InputField/InputField.tsx';
import useSubmitForm from '../../../../hooks/useSubmitForm.ts';
import {setIsAuth} from "../../../../redux/slices/authSlice.ts";
import {useDispatch, useSelector} from "react-redux";
import {useNavigate} from 'react-router-dom';
import {RootState} from "../../../../redux/store.ts";
import React from "react";
import {useTranslation} from "react-i18next";

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

    const {submitForm} = useSubmitForm('http://localhost:8000/api/v1/auth/login');

    const isAuthorized = useSelector((state:RootState) => state.auth.isAuthorized);

    const dispatch = useDispatch();

    const navigate = useNavigate();

    const [t] = useTranslation('global');

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
                message: error.message || t('auth.incorrectData'),
            });
        }
    };

    React.useEffect(() => {
      if (isAuthorized) {
          navigate('/');
      }
    })

    return (
        <main className={styles.container}>
            <div className={styles.login__box}>
                <h1>{t('auth.titleLogin')}</h1>
                <form onSubmit={handleSubmit(onSubmit)}>

                    {/*Email field*/}
                    <InputField
                        label={t('auth.username.label')}
                        type="text"
                        placeholder={t('auth.username.placeholder')}
                        register={register('username', {
                            required: t('auth.username.placeholder'),
                            pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                                message: t('auth.username.message'),
                            },
                        })}
                        error={errors.username}
                    />

                    {/*Password field*/}
                    <InputField
                        label={t('auth.password.label')}
                        type="password"
                        placeholder={t('auth.password.placeholder')}
                        register={register('password', {
                            required: t('auth.password.required'),
                            pattern: {
                                value: /^[A-Za-z\d@$!%*?&]{8,16}$/,
                                message: t('auth.password.message'),
                            },
                        })}
                        error={errors.password}
                    />
                    <button className={styles.submit__button} type="submit" disabled={isSubmitting}>
                        {isSubmitting ? t('auth.button.login.loading') : t('auth.button.login.static')}
                    </button>
                </form>
                <p className={styles.forgot__password}>{t('auth.forgotPassword')}</p>
            </div>
        </main>
    );
};

export default Login;
