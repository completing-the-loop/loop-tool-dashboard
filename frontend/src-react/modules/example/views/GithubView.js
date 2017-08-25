import React from 'react';
import Grid from 'react-bootstrap/lib/Grid';
import { Route } from 'react-router';
import GithubUserSearchView from './GithubUserSearchView';

export default function ({ match }) {
    return (
        <Grid>
            <Route path={`${match.url}/users`} component={GithubUserSearchView} />
        </Grid>
    );
}
