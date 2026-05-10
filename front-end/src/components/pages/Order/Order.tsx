import {SubmitHandler, useForm} from 'react-hook-form';
import InputField from '../../common/InputField/InputField.tsx';
import {useNavigate} from 'react-router-dom';
import {useTranslation} from "react-i18next";
import styles from './Order.module.scss'
import CartItem from "../../common/CartItem/CartItem.tsx";
import Button from "../../common/Button/Button.tsx";
import {apiClient, getAuthHeaders} from "../../../api/api.ts";
import {useAppSelector} from "../../../redux/hooks.ts";
import {useCurrencyFormatter} from "../../../hooks/useCurrencyFormatter.ts";
import SimilarItems from "../../common/SimilarItems/SimilarItems.tsx";

// Define the type for the order form
interface IFormOrder {
    email: string;
    street_name: string;
    street_number: string;
    apartment_number: string;
    zip_code: string;
    city: string;
    state: string;
    country: string;
    customer_notes?: string;
}

const Order = () => {
    const {
        register,
        handleSubmit,
        setError,
        formState: {errors, isSubmitting},
    } = useForm<IFormOrder>({mode: 'onChange'});

    const items = useAppSelector((state) => state.cart.items);
    const totalPrice = useAppSelector((state) => state.cart.total_price);

    const navigate = useNavigate();
    const [t] = useTranslation('global');
    const formatPrice = useCurrencyFormatter();

    const onSubmit: SubmitHandler<IFormOrder> = async (data) => {

        try {
            const response = await apiClient.post('/orders/', null, {
                params: data,
                headers: getAuthHeaders(),
            });

            if (response && response.status === 204) {
                navigate('/');
                return;
            }
        } catch {
            setError('email', {
                type: 'manual',
                message: t('order.error'),
            });
        }
    };

    return (
        <div className={styles.order__grid}>
            <main className={styles.container}>
                <div className={styles.order__box}>
                    <h2>{t('order.deliveryTitle')}</h2>
                    <form onSubmit={handleSubmit(onSubmit)}>
                        {/* Email Field */}
                        <InputField
                            label={t('order.email.label')}
                            type="text"
                            placeholder={t('order.email.placeholder')}
                            register={register('email', {
                                required: t('order.email.required'),
                                pattern: {
                                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                                    message: t('order.email.message'),
                                },
                            })}
                            error={errors.email}
                        />

                        {/* Street Name Field */}
                        <InputField
                            label={t('order.street_name.label')}
                            type="text"
                            placeholder={t('order.street_name.placeholder')}
                            register={register('street_name', {required: t('order.street_name.required')})}
                            error={errors.street_name}
                        />

                        {/* Street Number Field */}
                        <InputField
                            label={t('order.street_number.label')}
                            type="text"
                            placeholder={t('order.street_number.placeholder')}
                            register={register('street_number', {required: t('order.street_number.required')})}
                            error={errors.street_number}
                        />

                        {/* Apartment Number Field */}
                        <InputField
                            label={t('order.apartment_number.label')}
                            type="text"
                            placeholder={t('order.apartment_number.placeholder')}
                            register={register('apartment_number', {required: t('order.apartment_number.required')})}
                            error={errors.apartment_number}
                        />

                        {/* Zip Code Field */}
                        <InputField
                            label={t('order.zip_code.label')}
                            type="text"
                            placeholder={t('order.zip_code.placeholder')}
                            register={register('zip_code', {required: t('order.zip_code.required')})}
                            error={errors.zip_code}
                        />

                        {/* City Field */}
                        <InputField
                            label={t('order.city.label')}
                            type="text"
                            placeholder={t('order.city.placeholder')}
                            register={register('city', {required: t('order.city.required')})}
                            error={errors.city}
                        />

                        {/* State Field */}
                        <InputField
                            label={t('order.state.label')}
                            type="text"
                            placeholder={t('order.state.placeholder')}
                            register={register('state', {required: t('order.state.required')})}
                            error={errors.state}
                        />

                        {/* Country Field */}
                        <InputField
                            label={t('order.country.label')}
                            type="text"
                            placeholder={t('order.country.placeholder')}
                            register={register('country', {required: t('order.country.required')})}
                            error={errors.country}
                        />
                        <label className={styles.notesField}>
                            {t('order.notes.label')}
                            <textarea
                                placeholder={t('order.notes.placeholder')}
                                {...register('customer_notes', {
                                    maxLength: {
                                        value: 500,
                                        message: t('order.notes.message'),
                                    },
                                })}
                            />
                            {errors.customer_notes && (
                                <span>{errors.customer_notes.message}</span>
                            )}
                        </label>
                        <Button
                            label={isSubmitting ? t('order.button.loading') : t('order.button.submit')}
                            type="submit"
                            variant="primary"
                            disabled={isSubmitting}
                        />

                    </form>
                </div>
            </main>
            <aside>
                <h2>{t('order.orderTitle')}</h2>
                {items.length > 0 ? (
                    items.map((item) =>
                        <CartItem key={item.product_id}
                                  product_id={item.product_id}
                                  name={item.name}
                                  price={item.price}
                                  count={item.count}
                                  image_src={item.image_src}
                                  isOrder={true}
                                  isEditable={true}/>)
                ) : (
                    <p className={styles.empty}>{t('order.empty')}</p>
                )}
                <h2>{t('order.subtotal.title')}</h2>
                <div className={styles.subtotal}>
                    <div className={styles.price}>
                        <p>{t('order.subtotal.items')}:</p>
                        <span>{formatPrice(totalPrice)}</span>
                    </div>
                    <div className={styles.price}>
                        <p>{t('order.subtotal.shipping')}:</p>
                        <span>{formatPrice(35)}</span>
                    </div>
                </div>
                <div className={styles.total}>
                    <h2>{t('order.total')}: </h2>
                    <span>{formatPrice(totalPrice + 35)}</span>
                </div>
                <SimilarItems productIds={items.map((item) => item.product_id)} />
            </aside>
        </div>
    );
};

export default Order;
