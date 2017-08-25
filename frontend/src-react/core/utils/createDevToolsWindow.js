import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import DevTools from '../../containers/DevToolsWindow';


export default function createDevToolsWindow(store) {
  /* eslint-disable */
  const win = window.open(
    null,
    'redux-devtools', // give it a name so it reuses the same window
    `width=400,height=${window.outerHeight},menubar=no,location=no,resizable=yes,scrollbars=no,status=no`
  );
  /* eslint-enable */

  // reload in case it's reusing the same window with the old content
    if (!win) {
    /* eslint-disable */
    console.error('You are trying to use Redux devtools in a new window but a new window could not be opened; it has probably been blocked!');
    /* eslint-enable */
    }
    win.location.reload();

  // wait a little bit for it to reload, then render
    setTimeout(() => {
    // Wait for the reload to prevent:
    // "Uncaught Error: Invariant Violation: _registerComponent(...):
    // Target container is not a DOM element."
        win.document.write('<div id="react-devtools-root"></div>');
        win.document.body.style.margin = '0';

        ReactDOM.render(
            <Provider store={store}>
                <DevTools />
            </Provider>
        , win.document.getElementById('react-devtools-root')
    );
    }, 10);
}
