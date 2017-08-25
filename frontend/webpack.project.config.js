'use strict';

const webpackGenericConfig = require('./webpack.generic.config');

const commonSettings = {
    // insert project-specific settings here
};

module.exports = {
    production:  () => webpackGenericConfig(Object.assign({environment: 'production'},  commonSettings)),
    development: (extraConfig = {}) => webpackGenericConfig(
        Object.assign({environment: 'development'}, extraConfig, commonSettings)),
};
