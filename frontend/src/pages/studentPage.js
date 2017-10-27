import Plotly from 'plotly';
import Vue from 'vue';
import { get } from '../api';
import RangeGraph from '../components/range_graph.vue';

const init = async (
    initialData,
) => {
    new Vue({
        el: '#student-page',
        data: {
            courseId: initialData.courseId,
            courseStart: initialData.courseStart,
            numWeeks: initialData.numWeeks,
            studentId: initialData.studentId,
            communications: [],
            assessments: [],
        },
        mounted: async function mounted() {
            this.getCommunications();
            this.getAssessment();
        },
        methods: {
            async getCommunications() {
                this.communications = await get(`${this.courseId}/student_communications/${this.studentId}`);
            },
            async getAssessment() {
                this.assessments = await get(`${this.courseId}/student_assessments/${this.studentId}`);
            },
        },
        components: {
            RangeGraph,
        },
    });
};

window.pages = window.pages || {};
window.pages.studentPage = {};
window.pages.studentPage.init = init;
