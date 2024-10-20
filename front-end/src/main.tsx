import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import App from './App'
import './index.scss'
import {BrowserRouter} from 'react-router-dom'
import {Provider} from 'react-redux'
import {store} from "./redux/store";
import {I18nextProvider} from "react-i18next";
import globalEn from './locales/en/translation.json';
import globalUa from './locales/ua/translation.json';
import i18next from "i18next";


i18next.init({
    interpolation: {escapeValue: false},
    lng: "ua",
    resources: {
        en: {
            global: globalEn
        },
        ua: {
            global: globalUa,
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
