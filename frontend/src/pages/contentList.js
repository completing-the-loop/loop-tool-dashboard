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
        el: '#course-content-list',
        data: {
            indentPixels: window.__APP_CONTEXT__.PAGE_INDENT_PIXELS,
            courseId: initialData.courseId,
            numWeeks: initialData.numWeeks,
            pageViews: {
                pageSet: [],
                totalsByWeek: [],
            },
            students: {
                pageSet: [],
                totalsByWeek: [],
            },
            events: [],
            eventId: initialData.eventId,
        },
        mounted: async function mounted() {
            this.getPageViews();
            this.getStudents();
            this.getEvents();
        },
        computed: {
            sortedPageViews() {
                return this.sortedList(this.pageViews.pageSet);
            },
            sortedStudents() {
                return this.sortedList(this.students.pageSet);
            },
            sortedEvents() {
                return this.sortedList(this.events);
            },
        },
        methods: {
            expandAll(pageList) {
                const vue = this;
                _.forEach(pageList, function(page) {
                    vue.expandNode(pageList, page.id, true);
                });
            },
            collapseAll(pageList) {
                const vue = this;
                _.forEach(pageList, function(page) {
                    vue.collapseNode(pageList, page.id);
                });
            },
            expandNode(pageList, pageId, recursive=false) {
                if (!pageList[pageId].children.length || (pageList[pageId].expanded && !recursive)) {
                    return;
                }
                const vue = this;
                _.forEach(pageList[pageId].children, function(childId) {
                    pageList[childId].visible = true;
                    if (recursive) {
                        vue.expandNode(pageList, childId);
                    }
                });
                pageList[pageId].expanded = true;
            },
            collapseNode(pageList, pageId) {
                if (!pageList[pageId].children.length || !pageList[pageId].expanded) {
                    return;
                }
                const vue = this;
                _.forEach(pageList[pageId].children, function(childId) {
                    pageList[childId].visible = false;
                    vue.collapseNode(pageList, childId);
                });
                pageList[pageId].expanded = false;
            },
            toggleNode(pageList, pageId) {
                if (pageList[pageId].children.length) {
                    if (pageList[pageId].expanded) {
                        this.collapseNode(pageList, pageId);
                    } else {
                        this.expandNode(pageList, pageId);
                    }
                }
            },
            sortedList(pageList) {
                let sortedList = [];
                _.forEach(pageList, function(pageView) {
                    sortedList.push(pageView);
                });
                return _.orderBy(sortedList, ['sortOrder'], ['asc']);
            },

            setSortOrder(pageList, currentLevelPages, nextOrder, indentLevel) {
                const vue = this;
                _.forEach(currentLevelPages, function(pageId) {
                    pageList[pageId].indentLevel = indentLevel;
                    pageList[pageId].sortOrder = nextOrder;
                    nextOrder += 1;
                    if (pageList[pageId].children.length) {
                        nextOrder = vue.setSortOrder(pageList, pageList[pageId].children, nextOrder, indentLevel+1);
                    }
                });
                return nextOrder;
            },
            processPages(apiPageList) {
                const pageList = {};

                // Set the initial state parameters for each row
                _.forEach(apiPageList, function(page) {
                    page.expanded = false;
                    page.children = [];
                    page.sortOrder = 1;
                    page.indentLevel = 0;
                    if (!page.parentId) {
                        page.visible = true;
                    } else {
                        page.visible = false;
                    }
                    pageList[page.id] = page;
                });

                // Calculate the reverse relationship for parents
                const topLevelPages = [];
                _.forEach(pageList, function(page) {
                    if (page.parentId) {
                        pageList[page.parentId].children.push(page.id)
                    } else {
                        topLevelPages.push(page.id);
                    }
                });

                // Recursively set the sort order and indent level for correct display
                this.setSortOrder(pageList, topLevelPages, 1, 0);

                return pageList;
            },

            async getPageViews() {
                const apiPageViews = await get(`${this.courseId}/content_accesses/`);

                this.pageViews = apiPageViews;
                this.pageViews.pageSet = this.processPages(apiPageViews.pageSet);
            },
            async getStudents() {
                const apiStudents = await get(`${this.courseId}/content_students/`);

                this.students = apiStudents;
                this.students.pageSet = this.processPages(apiStudents.pageSet);
            },
            async getEvents() {
                const apiEvents = await get(`${this.courseId}/content_events/${this.eventId}/`);

                this.events = this.processPages(apiEvents);

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
                    };
                    const vue = this;

                    _.forEach(this.events, function(event) {
                        _.forEach(event.weeks, function(eventWeek, index) {
                            if (maxVisits) {
                                const pieProportion = (eventWeek[0] + eventWeek[1]) / maxVisits;
                                if (pieProportion) { // Skip graph if no views before and after event.
                                    const pieSize = pieProportion * (maxPieSize - minPieSize) + minPieSize;
                                    Plotly.newPlot(
                                        vue.$refs["pie_" + event.id][index],
                                        [Object.assign({}, pieData, {values: [eventWeek[0], eventWeek[1],],}),],
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
window.pages.contentList = {};
window.pages.contentList.init = init;
