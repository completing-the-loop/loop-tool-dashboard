import React, { Component } from 'react';
import FormGroup from 'react-bootstrap/lib/FormGroup';
import FormControl from 'react-bootstrap/lib/FormControl';
import ControlLabel from 'react-bootstrap/lib/ControlLabel';


const episodes = [
    {
        name: 'The Train Job',
    },
    {
        name: 'Bushwhacked',
    },
    {
        name: 'Our Mrs. Reynolds',
    },
    {
        name: 'Jaynestown',
    },
    {
        name: 'Out of Gas',
    },
    {
        name: 'Shindig',
    },
    {
        name: 'Safe',
    },
    {
        name: 'Ariel',
    },
    {
        name: 'War Stories',
    },
    {
        name: 'Objects in Space',
    },
    {
        name: 'Serenity (1)',
    },
    {
        name: 'Serenity (2)',
    },
    {
        name: 'Trash',
    },
    {
        name: 'The Message',
    },
    {
        name: 'Heart of Gold',
    },
];

export default class FilterListView extends Component {

    state = {
        searchKeywords: '',
    };

    handleFieldChange = ({ currentTarget: { value } }) => this.setState(() => ({ searchKeywords: value }));

    render() {
        const { searchKeywords } = this.state;
        const searchOnKeywords = ({ name }) => name.match(new RegExp(searchKeywords, 'i'));
        return (
            <div>
                <FormGroup controlId="search">
                    <ControlLabel>Search by name:</ControlLabel>
                    <FormControl
                        data-testId="searchKeywords"
                        value={this.state.searchKeywords}
                        type="text"
                        onChange={this.handleFieldChange}
                        autoComplete="off"
                    />
                </FormGroup>
                <ul data-testId="episodes">
                    {episodes.filter(searchOnKeywords).map((episode, i) =>
                        <li key={episode.name} data-testId="espisode">
                            {i + 1}. {episode.name}
                        </li>
                    )}
                </ul>
            </div>
        );
    }
}
