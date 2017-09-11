"use strict";
const webpack = require('webpack');
const express = require('express');
const webpackProjectConfig = require('./webpack.project.config');

const serverHost = '0.0.0.0';
const serverPort = '3011';

const webpackConfigDev = webpackProjectConfig.development({ serverHost, serverPort });

const compiler = webpack(webpackConfigDev);
// We use express with dev-middleware to get nice error overlay when developing
const app = express();
app.use(require('webpack-dev-middleware')(compiler, {
    noInfo: true,
    publicPath: webpackConfigDev.output.publicPath,
    headers: { "Access-Control-Allow-Origin": "*" },
}));

app.use(require('webpack-hot-middleware')(compiler));

app.all('/', function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With");
  next();
});

const server = app.listen(serverPort, serverHost, err => {
    if (err) {
        console.error(err);
        return;
    }
    console.log('Serving dev build on http://%s:%s.', server.address().address, server.address().port);
});
