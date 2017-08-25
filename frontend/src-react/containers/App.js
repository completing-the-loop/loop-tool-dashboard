import React from 'react';
import { injectEventListeners } from 'alliance-react';
import Nav from 'react-bootstrap/lib/Nav';
import Navbar from 'react-bootstrap/lib/Navbar';
import NavItem from 'react-bootstrap/lib/NavItem';
import { Route } from 'react-router';

import GithubView from '../modules/example/views/GithubView';
import FilterListView from '../modules/example/views/FilterListView';


class App extends React.Component {
    goRoute = (key) => {
        this.props.history.push(key);
    };
    render() {
        const { eventListeners } = this.props;
        return (
            <div style={{ height: '100%' }} {...eventListeners}>
                <Navbar inverse collapseOnSelect>
                    <Navbar.Header>
                        <Navbar.Brand>
                            Example Site
                        </Navbar.Brand>
                        <Navbar.Toggle />
                    </Navbar.Header>
                    <Navbar.Collapse>
                        <Nav onSelect={this.goRoute}>
                            <NavItem eventKey="/github/users">Github User Search</NavItem>
                            <NavItem eventKey="/filter-list">Filter List Test</NavItem>
                        </Nav>
                    </Navbar.Collapse>
                </Navbar>
                <Route path="/github" component={GithubView} />
                <Route path="/filter-list" component={FilterListView} />
            </div>
        );
    }
}

export default injectEventListeners()(App);
