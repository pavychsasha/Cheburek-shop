import axios, {AxiosResponse} from 'axios';
import {apiClient} from "../api/api.ts";

type SubmitFormResult = {
    res: AxiosResponse | null;
    error: {message?: string; detail?: string} | string | null;
};

const useSubmitForm = (endpoint: string) => {
    const contentTypeHeader: string = !endpoint.includes('login') ? 'application/json' : 'application/x-www-form-urlencoded'

    const submitForm = async (data: Record<string, unknown>): Promise<SubmitFormResult> => {
        try {
            const response = await apiClient.post(endpoint, data, {
                headers: {
                    'Content-Type': contentTypeHeader,
                },
            });
            return {res: response, error: null};
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                return {res: null, error: error.response.data};
            } else {
                return {res: null, error: 'Request failed'};
            }
        }
    };

    return {submitForm};
};

export default useSubmitForm;
