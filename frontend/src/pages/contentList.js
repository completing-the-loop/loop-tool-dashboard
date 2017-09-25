import Vue from 'vue';
import _ from 'lodash';
import { get } from '../api';

const init = async (
    courseId,
    numWeeks,
    eventId,
) => {
    new Vue({
        el: '#course-content-list',
        data: {
            courseId: courseId,
            numWeeks: numWeeks,
            pageViews: {},
            students: {},
            events: {},
            eventId: eventId,
        },
        mounted: async function mounted() {
            this.getPageViews();
            this.getStudents();
            this.getEvents();
        },
        computed: {
            sortedPageViews() {
                return this.sortedList(this.pageViews);
            },
            sortedStudents() {
                return this.sortedList(this.students);
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
                console.log('Expanded ' + pageId);
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
                console.log('Collapsed ' + pageId);
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

            async getPageViews() {
                this.pageViews = {
                    1: {
                        id: 1,
                        title: 'Page 1',
                        children: [],
                        module: 'module',
                        weeks: {
                            1: 0,
                            2: 1,
                            3: 6,
                            4: 7,
                            5: 3,
                            6: 8,
                            7: 4,
                            8: 22,
                            9: 11,
                            10: 12,
                            11: 33,
                            12: 7,
                            13: 4,
                            14: 7
                        },
                        total: 72,
                        percent: 91,
                        visible: true,
                        expanded: false,
                        sortOrder: 1,
                        indentLevel: 0,
                    },
                    2: {
                        id: 2,
                        title: 'Page 2',
                        children: [4, 5],
                        module: 'module',
                        weeks: {
                            1: 0,
                            2: 1,
                            3: 6,
                            4: 7,
                            5: 3,
                            6: 8,
                            7: 4,
                            8: 22,
                            9: 11,
                            10: 12,
                            11: 33,
                            12: 7,
                            13: 4,
                            14: 7
                        },
                        total: 72,
                        percent: 91,
                        visible: true,
                        expanded: false,
                        sortOrder: 2,
                        indentLevel: 0,
                    },
                    3: {
                        id: 3,
                        title: 'Page 3',
                        children: [6],
                        module: 'module',
                        weeks: {
                            1: 0,
                            2: 1,
                            3: 6,
                            4: 7,
                            5: 3,
                            6: 8,
                            7: 4,
                            8: 22,
                            9: 11,
                            10: 12,
                            11: 33,
                            12: 7,
                            13: 4,
                            14: 7
                        },
                        total: 72,
                        percent: 91,
                        visible: true,
                        expanded: false,
                        sortOrder: 5,
                        indentLevel: 0,
                    },
                    4: {
                        id: 4,
                        title: 'Page 2a',
                        children: [],
                        module: 'module',
                        weeks: {
                            1: 0,
                            2: 1,
                            3: 6,
                            4: 7,
                            5: 3,
                            6: 8,
                            7: 4,
                            8: 22,
                            9: 11,
                            10: 12,
                            11: 33,
                            12: 7,
                            13: 4,
                            14: 7
                        },
                        total: 72,
                        percent: 91,
                        visible: false,
                        expanded: false,
                        sortOrder: 3,
                        indentLevel: 19,
                    },
                    5: {
                        id: 5,
                        title: 'Page 2b',
                        children: [],
                        module: 'module',
                        weeks: {
                            1: 0,
                            2: 1,
                            3: 6,
                            4: 7,
                            5: 3,
                            6: 8,
                            7: 4,
                            8: 22,
                            9: 11,
                            10: 12,
                            11: 33,
                            12: 7,
                            13: 4,
                            14: 7
                        },
                        total: 72,
                        percent: 91,
                        visible: false,
                        expanded: false,
                        sortOrder: 4,
                        indentLevel: 19,
                    },
                    6: {
                        id: 6,
                        title: 'Page 3a',
                        children: [7],
                        module: 'module',
                        weeks: {
                            1: 0,
                            2: 1,
                            3: 6,
                            4: 7,
                            5: 3,
                            6: 8,
                            7: 4,
                            8: 22,
                            9: 11,
                            10: 12,
                            11: 33,
                            12: 7,
                            13: 4,
                            14: 7
                        },
                        total: 72,
                        percent: 91,
                        visible: false,
                        expanded: false,
                        sortOrder: 6,
                        indentLevel: 19,
                    },
                    7: {
                        id: 7,
                        title: 'Page 3ai',
                        children: [],
                        module: 'module',
                        weeks: {
                            1: 0,
                            2: 1,
                            3: 6,
                            4: 7,
                            5: 3,
                            6: 8,
                            7: 4,
                            8: 22,
                            9: 11,
                            10: 12,
                            11: 33,
                            12: 7,
                            13: 4,
                            14: 7
                        },
                        total: 72,
                        percent: 91,
                        visible: false,
                        expanded: false,
                        sortOrder: 7,
                        indentLevel: 38,
                    },
                };
            },
            async getStudents() {
                this.students = [
                    {page_id: 1, title: 'Page 1', module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},

                ];
            },
            async getEvents() {
                this.events = [
                    {
                        page_id: 1,
                        title: 'Page 1',
                        module: 'module',
                        weeks: {
                            1: {before: 0, after: 4},
                            2: {before: 0, after: 4},
                            3: {before: 0, after: 4},
                            4: {before: 0, after: 4},
                            5: {before: 0, after: 4},
                            6: {before: 0, after: 4},
                            7: {before: 0, after: 4},
                            8: {before: 0, after: 4},
                            9: {before: 0, after: 4},
                            10: {before: 0, after: 4},
                            11: {before: 0, after: 4},
                            12: {before: 0, after: 4},
                            13: {before: 0, after: 4},
                            14: {before: 0, after: 4}
                        }
                    },
                ];
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
