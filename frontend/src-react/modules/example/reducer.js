import { Record, List } from 'typed-immutable';

import createReducer from '../../core/createReducer';

const GithubState = Record({
    favourites: List(String),
}, 'Github');

export default createReducer(GithubState, {
    GITHUB_USER_REMOVE_FAVOURITE(state, { payload }) {
        return state.update('favourites', favourites => favourites.filter(username => username !== payload.user.login));
    },
    GITHUB_USER_ADD_FAVOURITE(state, { payload }) {
        return state.update('favourites', (favourites) => {
            if (favourites.contains(payload.user.login)) {
                return favourites;
            }
            return favourites.push(payload.user.login);
        });
    },
});
