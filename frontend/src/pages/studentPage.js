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
            this.getCommunications();
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
            async getCommunications() {
                this.communications = await get(`${this.courseId}/student_communications/${this.studentId}`);
            },
            async getAssessment() {
                this.assessments = await get(`${this.courseId}/student_assessments/${this.studentId}`);
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
