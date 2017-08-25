import { Record, Maybe } from 'typed-immutable';

import createReducer from '../../core/createReducer';

const AuthState = Record({
    isLoggedIn: Boolean(false),
    userId: Maybe(Number),
}, 'AuthState');

export default createReducer(AuthState, {
    // Unless you really need it only allow access to SPA if user is logged in
    // It simplifies a lot of things if you can always assume a user is logged
    // in. Otherwise fill in reducer here for handling login actions.
});
