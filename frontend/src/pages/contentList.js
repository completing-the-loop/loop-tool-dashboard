import Vue from 'vue';
import _ from 'lodash';
import { get } from '../api';

const init = async (
    initialData,
    indentPixels,
) => {
    new Vue({
        el: '#course-content-list',
        data: {
            indentPixels: window.__APP_CONTEXT__.INDENT_PIXELS,
            courseId: initialData.courseId,
            numWeeks: initialData.numWeeks,
            pageViews: {},
            students: {},
            events: {},
            eventId: initialData.eventId,
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
                const apiPageViews = [
                    {id: 1, title: 'Page 1', parentId: null, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 2, title: 'Page 2', parentId: null, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 3, title: 'Page 3', parentId: null, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 4, title: 'Page 2a', parentId: 2, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 5, title: 'Page 2b', parentId: 2, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 6, title: 'Page 3a', parentId: 3, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 7, title: 'Page 3ai', parentId: 6, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                ];

                this.pageViews = this.processPages(apiPageViews);
            },
            async getStudents() {
                const apiStudents = [
                    {id: 1, title: 'Page 1', parentId: null, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 2, title: 'Page 2', parentId: null, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 3, title: 'Page 3', parentId: null, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 4, title: 'Page 2a', parentId: 2, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 5, title: 'Page 2b', parentId: 2, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 6, title: 'Page 3a', parentId: 3, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                    {id: 7, title: 'Page 3ai', parentId: 6, module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},
                ];

                this.students = this.processPages(apiStudents);
            },
            async getEvents() {
                const apiEvents = [
                    {
                        id: 1,
                        title: 'Page 1',
                        module: 'module',
                        parentId: null,
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
                    {
                        id: 2,
                        title: 'Page 2',
                        module: 'module',
                        parentId: null,
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
                    {
                        id: 3,
                        title: 'Page 1a',
                        module: 'module',
                        parentId: 1,
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
                this.events = this.processPages(apiEvents);
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
