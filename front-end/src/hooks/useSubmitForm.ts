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
            return {res: response, error: null};
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                console.error('Error response data:', error.response.data);
                return {res: null, error: error.response.data};
            } else {
                console.error('Error message:', error);
                return {res: null, error: 'Проблема із запитом'};
            }
        }
    };

    return {submitForm};
};

export default useSubmitForm;
