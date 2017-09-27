import Vue from 'vue';
import { get } from '../api';

const init = async (
    courseId,
    courseWeeks,
    eventId,
) => {
    new Vue({
        el: '#communication',
        data: {
            courseId: courseId,
            courseWeeks: courseWeeks,
            accesses: [],
            posts: [],
            students: [],
            events: [],
            eventId: eventId,
        },
        mounted: async function mounted() {
            this.getAccesses();
            this.getPosts();
            this.getStudents();
            this.getEvents();
        },
        methods: {
            async getAccesses() {
                this.accesses = [
                    {page_id: 1, title: 'Page 1', module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},

                ];
            },
            async getPosts() {
                this.posts = [
                    {page_id: 1, title: 'Page 1', module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},

                ];
            },
            async getStudents() {
                this.students = [
                    {page_id: 1, title: 'Page 1', module: 'module', weeks: {1: 0, 2: 1, 3: 6, 4: 7, 5: 3, 6: 8, 7:4, 8:22, 9: 11, 10:12, 11: 33, 12: 7, 13: 4, 14: 7}, total: 72, percent: 91},

                ];
            },
            async getEvents() {
                this.events = [
                    {page_id: 1, title: 'Page 1', module: 'module', weeks: {1: {before: 0, after: 4}, 2: {before: 0, after: 4}, 3: {before: 0, after: 4}, 4: {before: 0, after: 4}, 5: {before: 0, after: 4}, 6: {before: 0, after: 4}, 7: {before: 0, after: 4}, 8: {before: 0, after: 4}, 9: {before: 0, after: 4}, 10: {before: 0, after: 4}, 11: {before: 0, after: 4}, 12: {before: 0, after: 4}, 13: {before: 0, after: 4}, 14: {before: 0, after: 4}}},

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
window.pages.communication = {};
window.pages.communication.init = init;

