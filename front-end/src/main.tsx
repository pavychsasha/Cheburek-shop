import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import App from './App'
import './index.scss'
import {BrowserRouter} from 'react-router-dom'
import {Provider} from 'react-redux'
import {store} from "./redux/store";
import i18next from 'i18next'
import global_en from '../src/locales/en/translation.json';
import global_ukr from '../src/locales/ukr/translation.json';
import {I18nextProvider} from "react-i18next";

i18next.init({
    interpolation: {escapeValue: false},
    lng: 'en',
    resources: {
        en: {
            global: global_en
        },
        ukr: {
            global: global_ukr
        }
    }
})

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <I18nextProvider i18n={i18next}>
            <BrowserRouter>
                <Provider store={store}>
                    <App/>
                </Provider>
            </BrowserRouter>
        </I18nextProvider>

    </StrictMode>
)
