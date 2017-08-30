import Vue from 'vue';
import { get } from '../api';

const init = async (
    courseId,
) => {
    new Vue({
        el: '#course-dashboard',
        data: {
            courseId: courseId,
            topUsers: {},
        },
        mounted: async function mounted() {
            this.getTopUsers();
        },
        methods: {
            async getTopUsers() {
                // This is getting all users without page views rather than top users with page views filtered by week
                // as we need to refactor the olap models first. It's more to demo/test the Vue setup
                this.topUsers = await get(`${this.courseId}/course_users`);
            },
        },
    });
};

window.pages = window.pages || {};
window.pages.dashboard = {};
window.pages.dashboard.init = init;
