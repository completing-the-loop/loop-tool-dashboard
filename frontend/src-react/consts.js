import trim from 'lodash/trim';

export const BASE_URL = `${trim(window.__APP_CONTEXT__.baseUrl, '/')}/`; // eslint-disable-line
export const BASE_API_URL = `${BASE_URL}api/`;
