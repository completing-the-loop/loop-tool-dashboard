'use strict';

module.exports = ({
    // one of 'development' or 'production'
    environment,

    // undefined (use default), true (more verbose default), or webpack 'devtool' setting
    sourceMap = undefined,

    // Include settings for jQuery?
    jQuery = true,

    // Include settings for bootstrap-sass?
    bootstrap = true,
    // Add bootstrap to the sass includePath?
    // allows you to do cleaner imports, eg
    //      @import 'bootstrap/buttons';
    // Not done by default because it breaks IDE discoverability
    bootstrapSassIncludePath = false,

    // Include settings for react?
    react = true,

} = {}) => {
    const assert = require('assert');
    const path = require('path');
    const webpack = require("webpack");

    // TODO: verbose
    // TODO: dev server
    // TODO: BundleTracker for django
    // TODO: CommonsChunk plugin
    // TODO: bundle size stats
    // TODO: webpack-dashboard
    // TODO: vendor bundling?
        // TODO: set up bundles:
        // - common
        // - frontend/public/SPA
        // - backend/admin
    // TODO: react
    // TODO: vue
    // TODO: angular
    // TODO: css-module support
    // TODO: postcss
    // TODO: hot reloading
    // TODO: pngcrush for production
    // TODO: vanilla CSS handling
    // TODO: handle JS located in django apps
    // TODO: handle (S)CSS located in django apps

    // TODO: use webpack-node-externals?

    const FRONTEND_DIR = './';
    const NODE_MODULES_DIR = path.join(FRONTEND_DIR, 'node_modules') + '/';
    const OUTPUT_DIR_BASE = path.join(FRONTEND_DIR, 'dist') + '/';
    const OUTPUT_DIR_RELATIVE = `/${environment}/`;
    const INLINE_BINARY_DATA_LIMIT = 8192;

    assert(['development', 'production'].indexOf(environment) >= 0, '"environment" option is not valid');
    const isDev = environment != 'production';

    if (sourceMap === true)      sourceMap = isDev ? 'eval-source-map' : 'source-map';
    if (sourceMap === undefined) sourceMap = isDev ? 'eval-source-map' : 'hidden-source-map';


    // ----------------------------------------------------------------------
    // Base config
    let conf = {
        devtool: sourceMap,
        entry: './src/index.js',
        output: {
            path: path.join(__dirname, OUTPUT_DIR_BASE, OUTPUT_DIR_RELATIVE),
            filename: "[name].bundle.js",
            publicPath: '/static' + OUTPUT_DIR_RELATIVE,
        },
        module: {
            rules: [],
            noParse: /jquery/,
        },
        plugins: [],
    };


    // ------------------------------------------------------------------
    // Config that may be modified by options
    let sassIncludePaths = [];
    let babelPresets = [
        'es2015',
    ];
    let babelPlugins = [
        'transform-async-to-generator',
        'transform-runtime',
    ];
    let babelPluginsProd = [];

    // ----------------------------------------------------------------------
    if (react) {
        babelPresets.push('react');
        babelPluginsProd.push('babel-plugin-transform-react-remove-prop-types');
        babelPluginsProd.push('babel-plugin-transform-react-constant-elements');
    }

    // ----------------------------------------------------------------------
    // jQuery
    if (jQuery) {
        conf.plugins.push(new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        }));
    }

    // ----------------------------------------------------------------------
    // bootstrap (sass version)
    if (bootstrap) {
        if (bootstrapSassIncludePath) {
            const bootstrapAssetsPath = path.resolve(NODE_MODULES_DIR, './bootstrap-sass/assets');
            sassIncludePaths += [
                bootstrapAssetsPath + '/stylesheets/',
                bootstrapAssetsPath + '/fonts/',
            ];
        }
    }


    // ------------------------------------------------------------------

    // Binary files
    conf.module.rules.push({
        test: /\.(jpg|jpeg|png|gif|eot|svg|ttf|woff|woff2)$/,
        loader: 'url-loader',
        options: { limit: INLINE_BINARY_DATA_LIMIT }
    });

    // ------------------------------------------------------------------
    // JS
    conf.module.rules.push({
        test: /\.(js|jsx)$/,
        loader: 'babel-loader',
        exclude: [
            path.resolve(NODE_MODULES_DIR),
            // path.resolve(BUILD_DIR),
        ],
        options: {
            presets: babelPresets,
            plugins: babelPlugins,
            env: {
                development: {
                    plugins: [],
                    presets: [],
                },
                production: {
                    plugins: babelPluginsProd,
                    presets: [],
                },
            },
            babelrc: false,
            cacheDirectory: false
        },
    });

    conf.module.rules.push({
        test: /\.json$/,
        loader: 'json-loader'
    });

    // ------------------------------------------------------------------
    // CSS/SCSS
    const getCssLoader = (includeSass) => {
         const cssUse = [
            'css-loader',
            // 'postcss-loader',
        ];
        if (includeSass) {
            let sassLoader = {
                loader: 'sass-loader',
                options: {
                    includePaths: sassIncludePaths,
                },
            };
            // make things a little cleaner
            if (!sassLoader.options.includePaths.length) delete sassLoader.options.includePaths;
            if (!Object.keys(sassLoader.options).length) delete sassLoader.options;
            cssUse.push(sassLoader);
        }

        return isDev ? cssUse : ['style-loader', ...cssUse];
    };

    conf.module.rules.push({
        test: /\.(css)$/,
        use: getCssLoader(false),
    });

    conf.module.rules.push({
        test: /\.(scss)$/,
        use: getCssLoader(true),
    });
    return conf;
};
