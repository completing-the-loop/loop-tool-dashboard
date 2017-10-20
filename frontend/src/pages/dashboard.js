import moment from 'moment';
import Plotly from 'plotly';
import Vue from 'vue';
import { get } from '../api';

const init = async (
    initialData,
) => {
    new Vue({
        el: '#course-dashboard',
        data: {
            weekNum: 0,
            courseId: initialData.courseId,
            numWeeks: initialData.numWeeks,
            courseStart: initialData.courseStart,
            topUsers: {},
            topContent: [],
            topCommunications: [],
            topAssessments: [],
            overallVisits: [],
            perWeekVisits: [],
        },
        mounted: async function mounted() {
            this.getOverallDashboard();
        },
        computed: {
            weekStart: function() {
                return moment(this.courseStart).add(this.weekNum - 1, 'weeks').format('MMM D, YYYY');
            },
            weekEnd: function() {
                return moment(this.courseStart).add(this.weekNum, 'weeks').add(-1, 'days').format('MMM D, YYYY');
            },
        },
        methods: {
            async getOverallDashboard() {
                this.getTopContent();
                this.getTopCommunications();
                this.getTopAssessments();
                this.getTopUsers();
                this.plotOverallGraph();
                this.plotHistogram();
            },
            async getWeekDashboard(weekNum) {
                this.getTopContent(weekNum);
                this.getTopCommunications(weekNum);
                this.getTopAssessments(weekNum);
                this.getTopUsers(weekNum);
                this.plotPerWeekGraph(weekNum);
                this.plotWeekMetrics(weekNum);
                this.plotHistogram(weekNum);
            },
            async getTopContent(weekNum = null) {
                this.topContent = await get(`${this.courseId}/top_content/${weekNum ? weekNum + '/' : ''}`);
            },
            async getTopCommunications(weekNum = null) {
                this.topCommunications = await get(`${this.courseId}/top_communication/${weekNum ? weekNum + '/' : ''}`);
            },
            async getTopAssessments(weekNum = null) {
                this.topAssessments = await get(`${this.courseId}/top_assessments/${weekNum ? weekNum + '/' : ''}`);
            },
            async getTopUsers(weekNum = null) {
                // This is getting top users with page views filtered by week
                this.topUsers = await get(`${this.courseId}/top_users`);
            },
            async plotHistogram(weekNum = null) {
            },
            async plotOverallGraph() {
                this.overallVisits = await get(`${this.courseId}/overall_pagevisits`);

                let maxVisits = 0;
                const dates = [];
                const contentVisits = [];
                const communicationVisits = [];
                const assessmentVisits = [];
                const singleEventsData = [];
                const submissionEventsData = [];
                const singleEventsText = [];
                const submissionEventsText = [];

                // Initial loop through data for page views
                _.forEach(this.overallVisits, function(visit) {
                    dates.push(visit.day);
                    contentVisits.push(visit.contentVisits);
                    communicationVisits.push(visit.communicationVisits);
                    assessmentVisits.push(visit.assessmentVisits);
                    if (visit.contentVisits > maxVisits) {
                        maxVisits = visit.contentVisits;
                    }
                    if (visit.communicationVisits > maxVisits) {
                        maxVisits = visit.communicationVisits;
                    }
                    if (visit.assessmentVisits > maxVisits) {
                        maxVisits = visit.assessmentVisits;
                    }
                });

                // Second loop to build events data
                _.forEach(this.overallVisits, function(visit) {
                    if (visit.singleEvents.length) {
                        singleEventsData.push(maxVisits+1);
                        singleEventsText.push(_.join(visit.singleEvents, ', '));
                    } else {
                        singleEventsData.push(null);
                        singleEventsText.push(null);
                    }
                    if (visit.submissionEvents.length) {
                        submissionEventsData.push(maxVisits+1);
                        submissionEventsText.push(_.join(visit.submissionEvents, ', '));
                    } else {
                        submissionEventsData.push(null);
                        submissionEventsText.push(null);
                    }
                });

                const graphData = [
                    {
                        type: "scatter",
                        mode: "lines",
                        name: "Content",
                        x: dates,
                        y: contentVisits,
                    },
                    {
                        type: "scatter",
                        mode: "lines",
                        name: "Communication",
                        x: dates,
                        y: communicationVisits,
                    },
                    {
                        type: "scatter",
                        mode: "lines",
                        name: "Assessment",
                        x: dates,
                        y: assessmentVisits,
                    },
                    {
                        type: "scatter",
                        mode: "markers+text",
                        name: "Single Events",
                        x: dates,
                        y: singleEventsData,
                        text: singleEventsText,
                        textposition: "top center",
                    },
                    {
                        type: "scatter",
                        mode: "markers+text",
                        name: "Submission Events",
                        x: dates,
                        y: submissionEventsData,
                        text: submissionEventsText,
                        textposition: "top center",
                    },
                ];

                // Make the range slider range a bit longer to show shaded sidebars
                const rangeStart = moment(this.courseStart).add(-2, 'weeks').format('YYYY-MM-DD');
                const rangeEnd = moment(this.courseStart).add(this.numWeeks + 2, 'weeks').format('YYYY-MM-DD');

                const graphLayout = {
                    xaxis: {
                        rangeselector: {
                            buttons: [
                                {
                                    count: 1,
                                    label: '1m',
                                    step: 'month',
                                    stepmode: 'backward'
                                },
                                {
                                    count: 3,
                                    label: '3m',
                                    step: 'month',
                                    stepmode: 'backward'
                                },
                                {
                                    count: 6,
                                    label: '6m',
                                    step: 'month',
                                    stepmode: 'backward'
                                },
                                {
                                    count: 1,
                                    label: 'YTD',
                                    step: 'year',
                                    stepmode: 'todate'
                                },
                                {
                                    count: 1,
                                    label: '1y',
                                    step: 'year',
                                    stepmode: 'backward'
                                },
                                {
                                    step: 'All',
                                },
                            ],
                            y: 1.1,
                        },
                        rangeslider: {
                            thickness: 0.3,
                            range: [rangeStart, rangeEnd],
                        },
                        type: 'date',
                    },
                    yaxis: {
                        range: [0, maxVisits + 2],
                    }
                };

                const graphConfig = {
                    modeBarButtonsToRemove: [
                        'sendDataToCloud',
                    ],
                };

                Plotly.newPlot('overall_pageviews_chart',
                    graphData,
                    graphLayout,
                    graphConfig,
                );
            },
            async plotPerWeekGraph(weekNum) {
                this.perWeekVisits = await get(`${this.courseId}/weekly_page_visits/${weekNum}/`);
                const days = [];
                const contentVisits = [];
                const communicationVisits = [];
                const assessmentVisits = [];
                const uniqueVisits = [];
                const repeatingEvents = [];

                // Initial loop through data for page views
                _.forEach(this.perWeekVisits, function(visit) {
                    days.push(moment(visit.day).format('ddd'));
                    contentVisits.push(visit.contentVisits);
                    communicationVisits.push(visit.communicationVisits);
                    assessmentVisits.push(visit.assessmentVisits);
                    uniqueVisits.push(visit.uniqueVisits);
                    repeatingEvents.push(visit.repeatingEvents);
                });

                const tags = this.generateGraphTags(repeatingEvents);

                this.$nextTick(function() {
                    const graphLayout = {
                        margin: {
                            t: 20,
                            r: 20,
                            b: 20,
                            l: 20
                        },
                    };
                    const graphConfig = {
                        displayModeBar: false,
                    };

                    Plotly.newPlot(
                        'per_week_pageviews_chart',
                        [
                            {
                                x: days,
                                y: contentVisits,
                                mode: 'lines+markers',
                                name: 'Content',
                                fill: 'tozeroy',
                            },
                            {
                                x: days,
                                y: communicationVisits,
                                mode: 'lines+markers',
                                name: 'Communication',
                                fill: 'tozeroy',
                            },
                            {
                                x: days,
                                y: assessmentVisits,
                                mode: 'lines+markers',
                                name: 'Assessment',
                                fill: 'tozeroy',
                            },
                            {
                                x: days,
                                y: uniqueVisits,
                                mode: 'lines+markers',
                                name: 'Unique Pages',
                                fill: 'tozeroy',
                            },
                        ],
                        Object.assign({}, graphLayout, tags),
                        graphConfig,
                    );
                });
            },
            async plotWeekMetrics(weekNum) {
            },
            generateGraphTags(events) {
                const shapes = _.map(events, function(eventList, index) {
                    if (eventList.length) {
                        return {
                            type: 'line',
                            x0: index,
                            y0: 0,
                            x1: index,
                            y1: 1,
                            xref: 'x',
                            yref: 'paper',
                            line: {
                                width: 3,
                            }
                        }
                    }
                });
                const annotations = _.map(events, function(eventList, index) {
                    if (eventList.length) {
                        return {
                            x: index,
                            y: 1,
                            xref: 'x',
                            yref: 'paper',
                            text: _.join(eventList, ', '),
                            textangle: 90,
                            showarrow: false,
                            yanchor: 'top',
                            xshift: 10,
                        }
                    }
                });

                return {
                    shapes: shapes,
                    annotations: annotations,
                }
            },
        },
        watch: {
            weekNum: function (val) {
                if (val >= 1) {
                    this.getWeekDashboard(val)
                } else {
                    this.getOverallDashboard();
                }
            },
        },
    });
};

window.pages = window.pages || {};
window.pages.dashboard = {};
window.pages.dashboard.init = init;
