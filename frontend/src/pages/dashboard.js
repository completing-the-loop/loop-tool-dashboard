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
                            },
                            {
                                x: days,
                                y: communicationVisits,
                                mode: 'lines+markers',
                                name: 'Communication',
                            },
                            {
                                x: days,
                                y: assessmentVisits,
                                mode: 'lines+markers',
                                name: 'Assessment',
                            },
                            {
                                x: days,
                                y: uniqueVisits,
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
