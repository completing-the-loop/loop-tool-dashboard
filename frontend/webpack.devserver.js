"use strict";
const webpack = require('webpack');
const WebpackDevServer = require('webpack-dev-server');
const webpackProjectConfig = require('./webpack.project.config');

const webpackConfigDev = webpackProjectConfig.development();

new WebpackDevServer(webpack(webpackConfigDev), {
	publicPath: webpackConfigDev.output.publicPath,
	// hot: true,
	// inline: true,
	// historyApiFallback: true
}).listen(3011, '0.0.0.0', function (err, result) {
	if (err) console.log(err);
	console.log('Listening at 0.0.0.0:3011');
});
