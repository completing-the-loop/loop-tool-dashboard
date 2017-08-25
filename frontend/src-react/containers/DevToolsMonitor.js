import DockMonitor from 'redux-devtools-dock-monitor';

export default class Monitor extends DockMonitor {
    constructor(...args) {
        super(...args);
        console.info('Toggle Redux DevTools with CTRL-H, reposition with CTRL-Q'); //eslint-disable-line
    }
}
