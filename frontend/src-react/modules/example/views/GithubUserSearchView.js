import React, { Component } from 'react';
import { connect } from 'react-redux';
import Row from 'react-bootstrap/lib/Row';
import Col from 'react-bootstrap/lib/Col';
import Label from 'react-bootstrap/lib/Label';
import FormGroup from 'react-bootstrap/lib/FormGroup';
import FormControl from 'react-bootstrap/lib/FormControl';
import ListGroup from 'react-bootstrap/lib/ListGroup';
import ListGroupItem from 'react-bootstrap/lib/ListGroupItem';
import ControlLabel from 'react-bootstrap/lib/ControlLabel';
import HelpBlock from 'react-bootstrap/lib/HelpBlock';
import { Route, Link } from 'react-router-dom';
import { fetchEntities } from 'alliance-redux-api/lib/actions';
import debounce from 'lodash/debounce';
import { GithubUser } from '../model';
import GithubUserView from './GithubUserView';

class GithubUserSearchView extends Component {

    state = {
        userSearch: '',
        ids: [],
        searchPerformed: false,
        searching: false,
        error: false,
    };

    componentWillMount() {
    }

    constructor(props) {
        super(props);
        this.triggerSearch = debounce(async () => {
            this.setState(() => ({ error: false, searching: true, searchPerformed: false, ids: [] }));
            const { userSearch } = this.state;
            try {
                const { ids } = await this.props.fetchEntities(GithubUser, { q: userSearch }, { endpoint: 'https://api.github.com/search/users' });
                this.setState(() => ({ searching: false, searchPerformed: true, ids }));
            } catch (e) {
                console.error(e); // eslint-disable-line
                this.setState(() => ({ error: true, searching: false }));
            }
        }, 500);
    }

    handleFieldChange = ({ currentTarget: { value } }) => {
        this.setState(() => ({ userSearch: value }));
        this.triggerSearch();
    }

    render() {
        const { users, favourites } = this.props;
        const { ids, searching, error, searchPerformed } = this.state;
        const filteredUsers = ids.map(id => users.get(id));
        return (
            <div>
                <Row>
                    <FormGroup controlId="user">
                        <ControlLabel>Search by user:</ControlLabel>
                        <FormControl
                            data-testId="userSearch"
                            value={this.state.userSearch}
                            type="text"
                            onChange={this.handleFieldChange}
                        />
                        {favourites.size ?
                            <HelpBlock data-testId="favourites">
                                <strong>Favourites: </strong>
                                {favourites.map(user =>
                                    <Label style={{ marginRight: 5 }} bsStyle="info" key={user.login}>
                                        <Link to={`${this.props.match.url}/${user.login}`}>{user.login}</Link>
                                    </Label>
                                ).toList()}
                            </HelpBlock>
                            : null
                        }
                    </FormGroup>
                    {error && <p>Sorry, there was an error querying github</p>}
                </Row>
                <Row>
                    <Col md={6}>
                        {searching && <p>Please waiting... searching</p>}
                        {filteredUsers.length > 0 &&
                            <ListGroup data-testId="user-list">
                                {filteredUsers.map(user =>
                                    <ListGroupItem key={user.login} style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Link data-testId="user-link" to={`${this.props.match.url}/${user.login}`}>
                                            {user.login}
                                        </Link>
                                        <a href={user.html_url}>{user.html_url}</a>
                                    </ListGroupItem>
                                )}
                            </ListGroup>
                        }
                        {!searching && filteredUsers.length === 0 && searchPerformed && <p>No results found</p>}
                        {!searching && filteredUsers.length === 0 && !searchPerformed && <p>Enter user name above to search</p>}
                    </Col>
                    <Col md={6}>
                        <Route path={`${this.props.match.url}/:username`} component={GithubUserView} />
                    </Col>
                </Row>
            </div>
        );
    }

}

function mapStateToProps(state) {
    return {
        users: GithubUser.selectors.all(state),
        favourites: GithubUser.selectors.favourites(state),
    };
}

export default connect(mapStateToProps, { fetchEntities })(GithubUserSearchView);
