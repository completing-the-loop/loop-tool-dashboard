import { Maybe } from 'typed-immutable';
import Model from 'alliance-redux-api/lib/Model';
import { Id } from 'alliance-redux-api/lib/fieldTypes';

export const GithubUser = Model({
    id: Id,
    url: String,
    login: String,
    repos_url: String,
    avatar_url: String,
    // These ones below may not be available if results fetched as result
    // of hitting the search endpoint. Will be available if hitting main users
    // endpoint
    company: Maybe(String),
    followers: Maybe(Number),
    following: Maybe(Number),
    location: Maybe(String),
    name: Maybe(String),
    html_url: Maybe(String),
    public_repos: Maybe(Number),
}, 'githubUser', 'User', {
    endpoint: 'https://api.github.com/users',
    idFieldName: 'login',
    buildSelectors: ({ all }) => ({
        favourites: (state) => {
            const favourites = state.Github.favourites;
            return all(state).filter(user => favourites.contains(user.login));
        },
    }),
    transformResponse: data => (
        {
            ...data,
            results: data.items,
            count: data.total_count,
        }
    ),
});
