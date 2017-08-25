import React from 'react';
import { Provider } from 'react-redux';
import { ConnectedRouter } from 'react-router-redux';
import { Route } from 'react-router';

import App from './App';

export default class Root extends React.Component {

    addDevTools() {
        if (__DEBUG__) {
            if (__DEBUG_NEW_WINDOW__) {
                if (!window.devToolsExtension) {
                    require('../core/utils/createDevToolsWindow').default(this.props.store); // eslint-disable-line
                } else {
                    window.devToolsExtension.open();
                }
                return null;
            } else if (!window.devToolsExtension) {
                const DevTools = require('../containers/DevTools').default; // eslint-disable-line

                return <DevTools />;
            }
        }
        return null;
    }

    render() {
        return (
            <Provider store={this.props.store}>
                <div style={{ height: '100%' }}>
                    <ConnectedRouter history={this.props.history}>
                        <Route component={App} />
                    </ConnectedRouter>
                    {this.addDevTools()}
                </div>
            </Provider>
        );
    }
}
