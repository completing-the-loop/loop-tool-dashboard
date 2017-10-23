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
        el: '#students',
        data: {
            courseId: initialData.courseId,
            numWeeks: initialData.numWeeks,
            accesses: {
                pageSet: [],
                totalsByWeek: []
            },
            events: [],
            eventId: initialData.eventId,
        },
        mounted: async function mounted() {
            this.getAccesses();
            this.getEvents();
        },
        methods: {
            async getAccesses() {
                this.accesses = await get(`${this.courseId}/students_accesses/`);
            },
            async getEvents() {
                this.events = await get(`${this.courseId}/students_events/${this.eventId}/`);

                this.$nextTick(function () {
                    const maxEvents = this.events.highestCellValue;
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
                    };
                    const vue = this;

                    _.forEach(this.events.studentSet, function(student) {
                        _.forEach(student.weeks, function(studentWeek, index) {
                            if (maxEvents) {
                                const pieProportion = (studentWeek[0] + studentWeek[1]) / maxEvents;
                                if (pieProportion) { // Skip graph if no views before and after event.
                                    const pieSize = pieProportion * (maxPieSize - minPieSize) + minPieSize;
                                    Plotly.newPlot(
                                        vue.$refs["pie_" + student.id][index],
                                        [Object.assign({}, pieData, {values: [studentWeek[0], studentWeek[1],],}),],
                                        Object.assign({}, pieLayout, {width: pieSize, height: pieSize,}),
                                        pieConfig,
                                    );
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
window.pages.students = {};
window.pages.students.init = init;

