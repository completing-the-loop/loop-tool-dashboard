import moment from 'moment';
import Plotly from 'plotly';
import Vue from 'vue';
import { get } from '../api';
import RangeGraph from '../components/range_graph.vue';
import HistogramGraph from '../components/histogram_graph.vue';

const init = async (
    initialData,
) => {
    const COURSE_OVERALL_NUM_HISTOGRAM_BINS = window.__APP_CONTEXT__.COURSE_OVERALL_NUM_HISTOGRAM_BINS;
    const COURSE_WEEK_NUM_HISTOGRAM_BINS = window.__APP_CONTEXT__.COURSE_WEEK_NUM_HISTOGRAM_BINS;

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
            weekMetrics: {},
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
            histogramNumBins: function() {
                if (this.weekNum) {
                    return COURSE_WEEK_NUM_HISTOGRAM_BINS;
                } else {
                    return COURSE_OVERALL_NUM_HISTOGRAM_BINS;
                }
            },
        },
        methods: {
            async getOverallDashboard() {
                this.getTopContent();
                this.getTopCommunications();
                this.getTopAssessments();
                this.getTopUsers();
            },
            async getWeekDashboard(weekNum) {
                this.getTopContent(weekNum);
                this.getTopCommunications(weekNum);
                this.getTopAssessments(weekNum);
                this.getTopUsers(weekNum);
                this.plotPerWeekGraph(weekNum);
                this.plotWeekMetrics(weekNum);
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
                this.weekMetrics = await get(`${this.courseId}/weekly_metrics/${this.weekNum}/`);

                const days = [];
                const uniqueVisits = [];
                const students = [];
                const sessions = [];
                const avgSessionDuration = [];
                const avgSessionPageviews = [];

                _.forEach(this.weekMetrics, function(dayMetrics) {
                    days.push(moment(dayMetrics.day).format('ddd'));
                    uniqueVisits.push(dayMetrics.uniqueVisits);
                    students.push(dayMetrics.students);
                    sessions.push(dayMetrics.sessions);
                    avgSessionDuration.push(dayMetrics.avgSessionDuration);
                    avgSessionPageviews.push(dayMetrics.avgSessionPageviews);
                });

                this.$nextTick(function() {
                    this.plotMetricGraph('metrics_unique_visits', days, uniqueVisits);
                    this.plotMetricGraph('metrics_students', days, students);
                    this.plotMetricGraph('metrics_sessions', days, sessions);
                    this.plotMetricGraph('metrics_avg_session_duration', days, avgSessionDuration);
                    this.plotMetricGraph('metrics_avg_session_pageviews', days, avgSessionPageviews);
                });
            },
            plotMetricGraph(graphId, days, values) {
                    const graphLayout = {
                        margin: {
                            t: 10,
                            r: 10,
                            b: 10,
                            l: 10
                        },
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        showlegend: false,
                        hovermode: 'closest',
                        height: 60,
                        width: 120,
                        xaxis: {
                            visible: false,
                            fixedrange: true,
                        },
                        yaxis: {
                            visible: false,
                            fixedrange: true,
                        },
                    };
                    const graphConfig = {
                        displayModeBar: false,
                    };

                    Plotly.newPlot(
                        graphId,
                        [
                            {
                                x: days,
                                y: values,
                                mode: 'lines+markers',
                                fill: 'tozeroy',
                                hover: 'y',
                                line: {
                                    color: 'white',
                                },
                            },
                        ],
                        graphLayout,
                        graphConfig,
                    );
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
        components: {
            RangeGraph,
            HistogramGraph,
        },
    });
};

window.pages = window.pages || {};
window.pages.dashboard = {};
window.pages.dashboard.init = init;
