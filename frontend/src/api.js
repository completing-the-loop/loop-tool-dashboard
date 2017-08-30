import 'whatwg-fetch';
import map from 'lodash/map';
import trim from 'lodash/trim';
import invariant from 'invariant';
import startsWith from 'lodash/startsWith';
import identity from 'lodash/identity';
import { BASE_API_URL } from './consts';


function toQueryString(params, convertValue = identity) {
    return map(params, (value, key) =>
        `${encodeURIComponent(key)}=${encodeURIComponent(convertValue(value))}`).join('&');
}

function buildApiUrl(endPoint) {
    const [uri, query] = endPoint.split('?');
    let url = `${BASE_API_URL}${trim(uri, '/')}/`;
    if (query) {
        url += `?${query}`;
    }
    return url;
}

function isAbsUrl(maybeUrl) {
    return startsWith(maybeUrl, 'http://') || startsWith(maybeUrl, 'https://');
}

/**
 * Helper to get django CSRF token. Needs to be called on every request as
 * the token can change (ie. after you login it will change)
 * @return {String} token
 */
function getCsrfToken() {
    const cookieMatch = document.cookie.match(/csrftoken=(.*?)(?:$|;)/);
    if (cookieMatch.length > 1) {
        return cookieMatch[1];
    }
    console.error( // eslint-disable-line
        'CSRF cookie not set. Authentication can not take place. Please contact a developer.');
    return 'COOKIE NOT FOUND';
}

class ApiError extends Error {
    constructor(status, statusText, response) {
        super();
        this.name = 'ApiError';
        this.status = status;
        this.statusText = statusText;
        this.response = response;
        this.message = `${status} - ${statusText}`;
    }
}

function parseJSON(res) {
    const contentType = res.headers.get('Content-Type');

    if (contentType.indexOf('json')) {
        return res.json();
    }
    return Promise.resolve(res.statusText);
}

async function checkStatus(response) {
    if (response.ok) {
        return parseJSON(response);
    }
    throw new ApiError(response.status, response.statusText, await parseJSON(response));
}


/**
 * Call an endpoint. See @post() and @get() below for method helpers.
 *
 * If the request itself fails (eg. you provide an invalid actionType) then
 * only the request action type will be dispatched and it will be marked as
 * an error.
 *
 * Otherwise requestType will be dispatched followed by either successType
 * or failureType depending on status code response. By default these action
 * types are the same - you can differentiate in reducer if 'error' key is
 * set to true.
 *
 * @param {String} endpoint can be relative in which case it will be made
 * absolute with BASE_API_URL
 * @param {String} method
 * @param {Object?} data
 * @param {Object?} config
 */
export function callApi(endpoint, method, data) {
    method = method.toUpperCase(); // eslint-disable-line
    invariant(['GET', 'PUT', 'POST', 'DELETE', 'PATCH'].includes(method),
        `Invalid method '${method}' specified to callApi`
    );
    if (!isAbsUrl(endpoint)) {
        endpoint = buildApiUrl(endpoint); // eslint-disable-line
    }
    const credentials = 'include';
    const body = data ? JSON.stringify(data) : null;
    const headers = {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRFToken': getCsrfToken(),
    };
    return fetch(endpoint, {
        method,
        body,
        credentials,
        headers,
    }).then(checkStatus);
}

const apiCallInProgressByEndpoint = {};

/**
 * Django rest framework filters in query parameters require booleans be
 * either True or False
 */
function convertDjangoQueryParam(value) {
    if (value === true) return 'True';
    if (value === false) return 'False';
    return value;
}

/**
 * For GET's don't fire same request multiple times
 */
export function get(endpoint, getParams = {}, config = {}) {
    invariant(endpoint.indexOf('?') === -1,
        `Call to get provided endpoint of ${endpoint} which contains a '?'. Pass ` +
        'any query parameters through as an object to the second parameter'
    );
    const finalEndpoint = [
        endpoint,
        // Convert query params into form expected by django-rest-framework
        // but only if we aren't dealing with absolute URL
        toQueryString(
            getParams,
            isAbsUrl(endpoint) ? identity : convertDjangoQueryParam
        ),
    ].join('?');
    if (apiCallInProgressByEndpoint[finalEndpoint]) {
        return apiCallInProgressByEndpoint[finalEndpoint];
    }
    apiCallInProgressByEndpoint[finalEndpoint] = callApi(finalEndpoint, 'get', null, config);
    return apiCallInProgressByEndpoint[finalEndpoint].then((result) => {
        delete apiCallInProgressByEndpoint[finalEndpoint];
        return result;
    });
}

export function post(endpoint, data = {}, config = {}) {
    return callApi(endpoint, 'post', data, config);
}

export function patch(endpoint, data = {}, config = {}) {
    return callApi(endpoint, 'patch', data, config);
}

export function del(endpoint, config = {}) {
    return callApi(endpoint, 'delete', null, config);
}
