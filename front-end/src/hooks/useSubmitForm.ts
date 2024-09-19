import axios from 'axios';

const useSubmitForm = (url: string) => {
    const contentTypeHeader: string = url.includes('register') ? 'application/json' : 'application/x-www-form-urlencoded'

    const submitForm = async (data: Record<string, any>) => {
        try {
            const response = await axios.post(url, data, {
                headers: {
                    'Content-Type': contentTypeHeader,
                },
            });
            console.log('Response:', response.data);
            return {data: response.data, error: null};
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                console.error('Error response data:', error.response.data);
                return {data: null, error: error.response.data};
            } else {
                console.error('Error message:', error);
                return {data: null, error: 'Проблема із запитом'};
            }
        }
    };

    return {submitForm};
};

export default useSubmitForm;
