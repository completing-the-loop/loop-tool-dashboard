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
                this.accesses = await get(`${this.courseId}/communication_accesses/`);
            },
            async getPosts() {
                this.posts = await get(`${this.courseId}/communication_posts/`);
            },
            async getStudents() {
                this.students = await get(`${this.courseId}/communication_students/`);
            },
            async getEvents() {
                this.events = await get(`${this.courseId}/communication_events/${this.eventId}/`);
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

