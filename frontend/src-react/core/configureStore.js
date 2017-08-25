import { combineReducers, applyMiddleware, compose, createStore } from 'redux';
import { routerMiddleware } from 'react-router-redux';
import { apiMiddleware } from 'redux-api-middleware';
import thunk from 'redux-thunk';

// import { authMiddleware } from '../modules/auth/middleware';
import * as reducers from './reducers';

let unsubscribeStore;

function withDevTools(middleware) {
    if (__DEBUG__) {
        const devTools = window.devToolsExtension
            ? window.devToolsExtension()
            : require('../containers/DevTools').default.instrument(); // eslint-disable-line
        return compose(middleware, devTools);
    }
    return middleware;
}

export default function configureStore({ initialState = {}, history }) {
    const middlewares = [
        thunk,
        routerMiddleware(history),
        apiMiddleware,
        // authMiddleware,
    ];
    let middleware = applyMiddleware(...middlewares);
    // Compose final middleware and use devtools in debug environment
    middleware = withDevTools(middleware); // eslint-disable-line no-undef

    // Create final store and subscribe router in debug env ie. for devtools
    const rootReducer = combineReducers(reducers);
    const store = createStore(rootReducer, initialState, middleware);

    // If we are hot loading this store we need this to clean up old subscriptions
    if (unsubscribeStore) unsubscribeStore();

    if (module.hot) { // eslint-disable-line
        // If reducers chang hotload them and replace the existing reducer
        module.hot.accept('./reducers', () => { // eslint-disable-line
            const nextRootReducer = require('./reducers'); // eslint-disable-line
            store.replaceReducer(combineReducers(nextRootReducer));
        });
    }

    return { store };
}
