import Plotly from 'plotly';
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
            topContent: {},
            topForumContent: [],
            topQuizContent: [],
        },
        mounted: async function mounted() {
            this.getTopContent();
            this.getTopForumContent();
            this.getTopQuizContent();
            this.getTopUsers();
            this.plotGraph();
        },
        methods: {
            async getTopContent() {
                this.topContent = [
                    {page_id: 1, title: 'Page 1', module: 'module', user_views: 7, page_views: 9},
                    {page_id: 2, title: 'Page 2', module: 'module', user_views: 4, page_views: 67},
                    {page_id: 3, title: 'Page 3', module: 'module', user_views: 6, page_views: 93},
                    {page_id: 4, title: 'Page 4', module: 'module', user_views: 2, page_views: 54},
                    {page_id: 5, title: 'Page 5', module: 'module', user_views: 5, page_views: 34},
                    {page_id: 6, title: 'Page 6', module: 'module', user_views: 8, page_views: 76},
                    {page_id: 7, title: 'Page 7', module: 'module', user_views: 5, page_views: 74},
                    {page_id: 8, title: 'Page 8', module: 'module', user_views: 4, page_views: 45},
                ];
            },
            async getTopForumContent() {
                this.topForumContent = [
                    {page_id: 11, title: 'Page 11', module: 'module', user_views: 6, page_views: 65, post_count: 12},
                    {page_id: 12, title: 'Page 12', module: 'module', user_views: 4, page_views: 86, post_count: 23},
                    {page_id: 13, title: 'Page 13', module: 'module', user_views: 2, page_views: 23, post_count: 32},
                    {page_id: 14, title: 'Page 14', module: 'module', user_views: 7, page_views: 37, post_count: 31},
                    {page_id: 15, title: 'Page 15', module: 'module', user_views: 7, page_views: 87, post_count: 13},
                    {page_id: 16, title: 'Page 16', module: 'module', user_views: 4, page_views: 23, post_count: 12},
                    {page_id: 17, title: 'Page 17', module: 'module', user_views: 3, page_views: 56, post_count: 14},
                    {page_id: 18, title: 'Page 18', module: 'module', user_views: 6, page_views: 45, post_count: 23},
                ];
            },
            async getTopQuizContent() {
                this.topQuizContent = [
                    {page_id: 21, title: 'Page 21', module: 'module', user_views: 6, average_score: 65, attempts: 12},
                    {page_id: 22, title: 'Page 22', module: 'module', user_views: 4, average_score: 86, attempts: 23},
                    {page_id: 23, title: 'Page 23', module: 'module', user_views: 2, average_score: 23, attempts: 32},
                    {page_id: 24, title: 'Page 24', module: 'module', user_views: 7, average_score: 37, attempts: 31},
                    {page_id: 25, title: 'Page 25', module: 'module', user_views: 7, average_score: 87, attempts: 13},
                    {page_id: 26, title: 'Page 26', module: 'module', user_views: 4, average_score: 23, attempts: 12},
                    {page_id: 27, title: 'Page 27', module: 'module', user_views: 3, average_score: 56, attempts: 14},
                    {page_id: 28, title: 'Page 28', module: 'module', user_views: 6, average_score: 45, attempts: 23},
                ];
            },
            async getTopUsers() {
                // This is getting top users with page views filtered by week
                this.topUsers = await get(`${this.courseId}/top_users`);
            },
            async plotGraph() {
                const data = [{
                    x: [1, 2, 3, 4, 5],
                    y: [1, 2, 4, 8, 16]
                }];
                Plotly.plot('graph_container', data, {margin: {t: 0}});
            },
        },
    });
};

window.pages = window.pages || {};
window.pages.dashboard = {};
window.pages.dashboard.init = init;
