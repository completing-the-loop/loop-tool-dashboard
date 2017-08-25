// Uncoment this for redux-form support
// export { reducer as form } from 'redux-form';
import createModelsReducer from 'alliance-redux-api/lib/createModelsReducer';
import reduceReducers from '../core/reduceReducers';
import { GithubUser } from '../modules/example/model';

export { default as Github } from '../modules/example/reducer';
export { default as Auth } from '../modules/auth/reducer';
export { routerReducer as router } from 'react-router-redux';

const Entities = reduceReducers(
    createModelsReducer(GithubUser)
);

export { Entities };
