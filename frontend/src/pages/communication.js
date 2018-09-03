import $ from "jquery";
import Vue from 'vue';
import _ from 'lodash';
import Plotly from 'plotly';

import { get } from '../api';

const init = async (
    initialData,
) => {
    const maxPieSize = window.__APP_CONTEXT__.PAGE_MAX_PIE_GRAPH_PIXELS;
    const minPieSize = window.__APP_CONTEXT__.PAGE_MIN_PIE_GRAPH_PIXELS;
    const pieBeforeColor = window.__APP_CONTEXT__.PAGE_PIE_CHART_BEFORE_COLOR;
    const pieAfterColor = window.__APP_CONTEXT__.PAGE_PIE_CHART_AFTER_COLOR;

    new Vue({
        el: '#course-communication',
        data: {
            courseId: initialData.courseId,
            numWeeks: initialData.numWeeks,
            accesses: {
                pageSet: [],
                totalsByWeek: []
            },
            posts: {
                pageSet: [],
                totalsByWeek: []
            },
            students: {
                pageSet: [],
                totalsByWeek: []
            },
            events: [],
            eventId: initialData.eventId,
        },
        mounted: async function mounted() {
            this.getAccesses();
            this.getPosts();
            this.getStudents();
            this.getEvents();
        },
        methods: {
            async getAccesses() {
                this.accesses = await get(`${this.courseId}/communication_accesses/`);
            },
            async getPosts() {
                this.posts = await get(`${this.courseId}/communication_posts/`);
            },
            async getStudents() {
                this.students = await get(`${this.courseId}/communication_students/`);
            },
            async getEvents() {
                if (this.eventId === null) {
                    return;
                }

                this.events = await get(`${this.courseId}/communication_events/${this.eventId}/`);

                this.$nextTick(function () {
                    let maxVisits = 0;
                    _.forEach(this.events, function(event) {
                        _.forEach(event.weeks, function (eventWeek) {
                            if (eventWeek[0] + eventWeek[1] > maxVisits) {
                                maxVisits = eventWeek[0] + eventWeek[1];
                            }
                        });
                    });

                    const pieLayout = {
                        showlegend: false,
                        autosize: false,
                        margin: {
                            l: 0,
                            r: 0,
                            t: 0,
                            b: 0,
                        },
                    };
                    const pieConfig = {
                        staticPlot: true,
                    };
                    const pieData = {
                        marker: {
                            colors: [pieBeforeColor, pieAfterColor],
                        },
                        type: 'pie',
                        textinfo: 'none',
                        hoverinfo: 'none',
                        labels: ['Before', 'After'],
                    };
                    const vue = this;

                    _.forEach(this.events, function(event) {
                        _.forEach(event.weeks, function(eventWeek, index) {
                            if (maxVisits) {
                                const pieProportion = (eventWeek[0] + eventWeek[1]) / maxVisits;
                                if (pieProportion) { // Skip graph if no views before and after event.
                                    const pieSize = pieProportion * (maxPieSize - minPieSize) + minPieSize;
                                    const plotDiv = vue.$refs["pie_" + event.id][index];
                                    const dataSeries = Object.assign({}, pieData, {values: [eventWeek[0], eventWeek[1],],});
                                    Plotly.newPlot(
                                        plotDiv,
                                        [dataSeries,],
                                        Object.assign({}, pieLayout, {width: pieSize, height: pieSize,}),
                                        pieConfig,
                                    );
                                    let tooltipText = '';
                                    const seriesTotal = _.reduce(dataSeries.values, function(sum, num) {
                                        return sum + num;
                                    });
                                    _.forEach(dataSeries.labels, function(label, index) {
                                        const percentage = Math.round(dataSeries.values[index] / seriesTotal * 100);
                                        tooltipText += `${label}: ${dataSeries.values[index]} (${percentage}%)<br />`
                                    });
                                    $(plotDiv).tooltip({
                                        toggle: 'tooltip',
                                        placement: 'auto top',
                                        trigger: 'hover',
                                        html: true,
                                        container: 'body',
                                        title: tooltipText,
                                    });
                                }
                            }
                        });
                    });
                });

            },
        },
        watch: {
            eventId: function (val) {
                this.getEvents();
            },
        },
    });
};

window.pages = window.pages || {};
window.pages.communication = {};
window.pages.communication.init = init;

