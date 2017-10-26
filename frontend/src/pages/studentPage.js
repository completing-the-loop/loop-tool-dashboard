import Plotly from 'plotly';
import Vue from 'vue';
import {get} from '../api';

const init = async (
    initialData,
) => {
    new Vue({
        el: '#student-page',
        data: {
            courseId: initialData.courseId,
            studentId: initialData.studentId,
            accesses: {},
            communications: [],
            assessments: [],
        },
        mounted: async function mounted() {
            this.getAccesses();
            this.getCommunication();
            this.getAssessment();
        },
        methods: {
            async getAccesses() {
                this.accesses = [
                    {date: '2017-06-01', accesses: 7},
                    {date: '2017-06-02', accesses: 3},
                    {date: '2017-06-07', accesses: 7},
                    {date: '2017-06-08', accesses: 8},
                    {date: '2017-06-10', accesses: 2},
                    {date: '2017-06-11', accesses: 4},
                    {date: '2017-06-15', accesses: 8},
                ];
            },
            async getCommunication() {
                this.communications = [
                    {page_id: 11, title: 'Page 11', module: 'module', page_views: 6, post_count: 65},
                    {page_id: 12, title: 'Page 12', module: 'module', page_views: 86, post_count: 23},
                    {page_id: 13, title: 'Page 13', module: 'module', page_views: 23, post_count: 32},
                    {page_id: 14, title: 'Page 14', module: 'module', page_views: 37, post_count: 31},
                    {page_id: 15, title: 'Page 15', module: 'module', page_views: 87, post_count: 13},
                    {page_id: 16, title: 'Page 16', module: 'module', page_views: 23, post_count: 12},
                    {page_id: 17, title: 'Page 17', module: 'module', page_views: 56, post_count: 14},
                    {page_id: 18, title: 'Page 18', module: 'module', page_views: 45, post_count: 23},
                ];
            },
            async getAssessment() {
                this.assessments = [
                    {page_id: 21, title: 'Page 21', module: 'module', page_views: 6, average_score: 65, attempts: 12},
                    {page_id: 22, title: 'Page 22', module: 'module', page_views: 4, average_score: 86, attempts: 23},
                    {page_id: 23, title: 'Page 23', module: 'module', page_views: 2, average_score: 23, attempts: 32},
                    {page_id: 24, title: 'Page 24', module: 'module', page_views: 7, average_score: 37, attempts: 31},
                    {page_id: 25, title: 'Page 25', module: 'module', page_views: 7, average_score: 87, attempts: 13},
                    {page_id: 26, title: 'Page 26', module: 'module', page_views: 4, average_score: 23, attempts: 12},
                    {page_id: 27, title: 'Page 27', module: 'module', page_views: 3, average_score: 56, attempts: 14},
                    {page_id: 28, title: 'Page 28', module: 'module', page_views: 6, average_score: 45, attempts: 23},
                ];
            },
            async plotGraph() {
                var accessSeries = {
                    type: "scatter",
                    mode: "lines",
                    name: 'Page Views',
                    x: this.accesses.map(function (x) {
                        return x.date;
                    }),
                    y: this.accesses.map(function (x) {
                        return x.accesses;
                    }),
                    line: {color: '#17BECF'}
                };

                var layout = {
                    xaxis: {
                        autorange: true,
                        range: [this.startDate, this.endDate],
                        rangeselector: {
                            buttons: [
                                {
                                    count: 1,
                                    label: '1m',
                                    step: 'month',
                                    stepmode: 'backward'
                                },
                                {
                                    count: 6,
                                    label: '6m',
                                    step: 'month',
                                    stepmode: 'backward'
                                },
                                {step: 'all'}
                            ]
                        },
                        rangeslider: {},
                        type: 'date'
                    },
                    yaxis: {
                        autorange: true,
                        type: 'linear'
                    },
                    margin: {
                        l: 0,
                        r: 0,
                        b: 0,
                        t: 0,
                        pad: 0
                    },
                };

                Plotly.newPlot('graph_container', [accessSeries], layout);
            },
        },
        watch: {
            accesses: function(val) {
                this.plotGraph();
            },
        },
    });
};

window.pages = window.pages || {};
window.pages.studentPage = {};
window.pages.studentPage.init = init;
