import styles from '../Auth.module.scss';
import {SubmitHandler, useForm} from 'react-hook-form';
import InputField from '../../../common/InputField/InputField.tsx';
import useSubmitForm from '../../../../hooks/useSubmitForm.ts';
import {setIsAuth} from "../../../../redux/slices/authSlice.ts";
import {NavLink, useNavigate} from "react-router-dom";
import {useTranslation} from "react-i18next";
import React from "react";
import {useAppDispatch, useAppSelector} from "../../../../redux/hooks.ts";

//Type(interface) of register form
interface IFormRegister {
    email: string;
    password: string;
    rePassword: string;
    username: string;
}

const Register = () => {

    //Parameters for a register form
    const {
        register,
        handleSubmit,
        setError,
        formState: {errors, isSubmitting},
        getValues,
    } = useForm<IFormRegister>({mode: 'onChange'});

    const {submitForm: submitRegisterForm} = useSubmitForm('/auth/register');
    const {submitForm: submitLoginForm} = useSubmitForm('/auth/login');

    const dispatch = useAppDispatch();

    const isAuthorized = useAppSelector((state) => state.auth.isAuthorized);

    const navigate = useNavigate();

    const [t] = useTranslation('global');

    const onSubmit: SubmitHandler<IFormRegister> = async (data) => {

        //User data for register
        const {res: regResponse, error: regError} = await submitRegisterForm({
            email: data.email,
            password: data.password,
            username: data.username
        });

        //Checking for response /auth/register
        if (regResponse && regResponse.status === 201) {
            const {res: logResponse, error: logError} = await submitLoginForm({

                //User data for login
                grant_type: '',
                username: data.email,
                password: data.password,
                scope: '',
                client_id: '',
                client_secret: '',
            });

            //Checking for response /auth/login
            if (logResponse && logResponse.status === 200) {
                const token = logResponse.data.access_token;
                localStorage.setItem('token', token);
                dispatch(setIsAuth(true));
                navigate('/');
            } else if (logError) {
                setError('rePassword', {
                    type: 'manual',
                    message: typeof logError === 'string' ? logError : logError.message || logError.detail || t('auth.registrationFailed'),
                });
            }
        } else if (regError) {
            setError('rePassword', {
                type: 'manual',
                message: typeof regError === 'string' ? regError : regError.message || regError.detail || t('auth.userExist'),
            });
        }
    };

    React.useEffect(() => {
        if (isAuthorized) {
            navigate('/');
        }
    }, [isAuthorized, navigate])

    return (
        <main className={styles.container}>
            <div className={styles.login__box}>
                <NavLink className={styles.backLink} to="/">
                    {t('auth.backToMenu')}
                </NavLink>
                <h1>{t('auth.titleRegister')}</h1>
                <form onSubmit={handleSubmit(onSubmit)}>

                    {/*Email field*/}
                    <InputField
                        label={t('auth.email.label')}
                        type="email"
                        placeholder={t('auth.email.placeholder')}
                        register={register('email', {
                            required: t('auth.email.required'),
                            pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                                message: t('auth.email.message'),
                            },
                        })}
                        error={errors.email}
                    />

                    {/*Username field*/}
                    <InputField
                        label={t('auth.username.label')}
                        type="text"
                        placeholder={t('auth.username.placeholder')}
                        register={register('username', {
                            required: t('auth.username.required'),
                            pattern: {
                                value: /^[A-Z0-9._%+-]{3,16}$/i,
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

                    {/*RePassword field*/}
                    <InputField
                        label={t('auth.rePassword.label')}
                        type="password"
                        placeholder={t('auth.rePassword.placeholder')}
                        register={register('rePassword', {
                            required: t('auth.rePassword.required'),
                            validate: (value) => value === getValues('password') || t('auth.passwordMatch'),
                        })}
                        error={errors.rePassword}
                    />
                    <button className={styles.submit__button} type="submit" disabled={isSubmitting}>
                        {isSubmitting ? t('auth.button.register.loading') : t('auth.button.register.static')}
                    </button>
                </form>

                {/*Redirect to login page*/}
                <NavLink to={'/login'}><p className={styles.forgot__password}>{t('auth.haveAccount')}</p></NavLink>
            </div>
        </main>
    );
};

export default Register;
