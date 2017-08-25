import React from 'react';
import { createDevTools } from 'redux-devtools';
import LogMonitor from 'redux-devtools-log-monitor';
import DevToolsMonitor from './DevToolsMonitor';

export default createDevTools(
    <DevToolsMonitor
        defaultIsVisible={false}
        toggleVisibilityKey="ctrl-h"
        changePositionKey="ctrl-q"
    >
        <LogMonitor />
    </DevToolsMonitor>
);
