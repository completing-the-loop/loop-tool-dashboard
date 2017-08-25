import React from 'react';
import { AppContainer } from 'react-hot-loader';
import { render } from 'react-dom';
import createHistory from 'history/createBrowserHistory';
import { configureApi } from 'alliance-redux-api/lib/api';

import { BASE_API_URL } from './consts';
import configureStore from './core/configureStore';
import Root from './containers/Root';

import './styles/main.scss';

configureApi(BASE_API_URL, { includeCsrfTokenHeader: true });
configureApi('https://api.github.com', {
    includeCsrfTokenHeader: false,
    appendSlash: false,
    isDefault: false,
    credentials: undefined,
});

const history = createHistory({
    // Specify different basename here if required
    // basename: '/frontend' /
});

const appContext = window.__APP_CONTEXT__; // eslint-disable-line
const initialState = appContext.initialState;
const { store } = configureStore({
    initialState,
    history,
});

render(
    <AppContainer>
        <Root history={history} store={store} />
    </AppContainer>,
    document.getElementById('root')
);


if (module.hot) { // eslint-disable-line
    module.hot.accept('./containers/Root', () => { // eslint-disable-line
        const ReplaceRoot = require('./containers/Root').default; // eslint-disable-line
        render(
            <AppContainer>
                <ReplaceRoot history={history} store={store} />
            </AppContainer>,
           document.getElementById('root')
       );
    });
}
