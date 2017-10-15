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
            perWeekData: {},
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
            },
            async plotPerWeekGraph(weekNum) {
                this.perWeekData = {
                    events: [
                        ['Lecture'], [], ['Tutorial', 'Other'], [], [], [], [],
                    ],
                    days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun',],
                    content: [ 1 * this.weekNum, 2, 3, 4, 5, 6, 7],
                    communications: [2, 3, 4, 5, 6, 7, 1],
                    assessments: [3, 4, 5, 6, 7, 1, 2],
                    unique: [4, 5, 6, 7, 1, 2, 3],
                };

                const tags = this.generateGraphTags(this.perWeekData.events);

                this.$nextTick(function() {
                    const graphLayout = {
                        margin: {t: 20, r: 20, b: 20, l: 20},
                    };
                    const graphConfig = {
                        displayModeBar: false,
                    };

                    Plotly.newPlot(
                        'graph_container',
                        [
                            {
                                x: this.perWeekData.days,
                                y: this.perWeekData.content,
                                mode: 'lines+markers',
                                name: 'Content',
                            },
                            {
                                x: this.perWeekData.days,
                                y: this.perWeekData.communications,
                                mode: 'lines+markers',
                                name: 'Communication',
                            },
                            {
                                x: this.perWeekData.days,
                                y: this.perWeekData.assessments,
                                mode: 'lines+markers',
                                name: 'Assessment',
                            },
                            {
                                x: this.perWeekData.days,
                                y: this.perWeekData.unique,
                                mode: 'lines+markers',
                                name: 'Unique Pages',
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
                                color: 'rgb(55, 128, 191)',
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
