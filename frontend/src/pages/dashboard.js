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

                const dates = _.map(this.overallVisits, function(visit) {
                    return visit.day;
                });
                const communicationVisits = _.map(this.overallVisits, function(visit) {
                    return visit.communicationVisits;
                });
                const contentVisits = _.map(this.overallVisits, function(visit) {
                    return visit.contentVisits;
                });
                const assessmentVisits = _.map(this.overallVisits, function(visit) {
                    return visit.assessmentVisits;
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
                ];
                const graphLayout = {
                    margin: {
                        t: 0,
                    },
                };
                Plotly.newPlot('overall_pageviews_chart',
                    graphData,
                    graphLayout,
                );

            },
            async plotPerWeekGraph(weekNum) {
                const data = [{
                    x: [1, 2, 3, 4, 5],
                    y: [1, 2, 4, 8, 16]
                }];
                Plotly.plot('graph_container', data, {margin: {t: 0}});
            },
            async plotWeekMetrics(weekNum) {
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
