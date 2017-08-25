import React from 'react';
import { Route } from 'react-router';

import App from './containers/App';
import PageNotFound from './screens/PageNotFound';

export default function (/* config */) {
    return (
        <Route component={App}>
            <Route path="*" component={PageNotFound} />
        </Route>
    );
}
