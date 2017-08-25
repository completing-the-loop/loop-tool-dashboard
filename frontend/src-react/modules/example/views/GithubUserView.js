import React, { Component } from 'react';
import Image from 'react-bootstrap/lib/Image';
import Badge from 'react-bootstrap/lib/Badge';
import Button from 'react-bootstrap/lib/Button';
import Glyphicon from 'react-bootstrap/lib/Glyphicon';
import { connect } from 'react-redux';
import { fetchEntity } from 'alliance-redux-api/lib/actions';
import { GithubUser } from '../model';
import { addUserToFavourites, removeUserFromFavourites } from '../actions';

class GithubUserView extends Component {

    state = {
        isLoading: true,
    };

    componentWillReceiveProps(nextProps) {
        if (nextProps.match.params.username !== this.props.match.params.username) {
            this.fetchUser(nextProps.match.params.username);
        }
    }

    componentWillMount() {
        this.fetchUser(this.props.match.params.username);
    }

    async fetchUser(username) {
        try {
            this.setState(() => ({ isLoading: true, error: false, notFound: false }));
            await this.props.fetchEntity(GithubUser, username, { nocache: true });
            this.setState(() => ({ isLoading: false }));
        } catch (e) {
            if (e && e.status === 404) {
                this.setState(() => ({ notFound: true, isLoading: false }));
            } else {
                this.setState(() => ({ error: true, isLoading: false }));
            }
        }
    }

    toggleFavourite = () => {
        const fn = this.props.isFavourite ? this.props.removeUserFromFavourites : this.props.addUserToFavourites;
        fn(this.props.user);
    };

    render() {
        const { notFound, error, isLoading } = this.state;
        if (notFound) {
            return <div>Sorry, that user was not found.</div>;
        }
        if (error) {
            return <div>Sorry, there was a problem fetching user.</div>;
        }
        if (isLoading) {
            return <div>Please wait.... loading</div>;
        }
        const { user, isFavourite } = this.props;
        return (
            <div style={{ width: 200, textAlign: 'center', border: '1px solid #ccc', padding: 20, borderRadius: 5 }}>
                <Image style={{ width: 100 }} src={user.avatar_url} circle />
                <h3><a href={user.html_url}>{user.name || user.login}</a></h3>
                <p>
                    <Button onClick={this.toggleFavourite} data-testId="favourite">
                        <Glyphicon glyph="star" />
                        {isFavourite ? 'Remove Favourite' : 'Add Favourite'}
                    </Button>
                </p>
                <div style={{ textAlign: 'left' }}>
                    <p>
                        <Badge data-testId="repo-count">{user.public_repos}</Badge> Repos
                    </p>
                    <p>
                        <Badge data-testId="follower-count">{user.followers}</Badge> Followers
                    </p>
                </div>
            </div>
        );
    }
}

function mapStateToProps(state, props) {
    const { match: { params } } = props;
    return {
        user: GithubUser.selectors.all(state).get(params.username),
        isFavourite: !!GithubUser.selectors.favourites(state).get(params.username),
    };
}

export default connect(mapStateToProps, { fetchEntity, addUserToFavourites, removeUserFromFavourites })(GithubUserView);
