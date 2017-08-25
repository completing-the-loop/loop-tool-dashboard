/*
 * Commented out as depends on alliance-redux-api - add back as required
import { API_CALL_AUTH_REQUIRED } from 'alliance-redux-api/lib/api';

export function authMiddleware() {
    return next => (action) => {
        if (action.type === API_CALL_AUTH_REQUIRED) {
            // Force reload to trigger login flow
            window.location.reload();
            return null;
        }
        return next(action);
    };
}
*/
