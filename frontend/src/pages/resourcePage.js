import Vue from 'vue';
import { get } from '../api';
import RangeGraph from '../components/range_graph.vue';

const init = async (
    initialData,
) => {
    new Vue({
        el: '#resource-page',
        data: {
            courseId: initialData.courseId,
            courseStart: initialData.courseStart,
            numWeeks: initialData.numWeeks,
            resourceId: initialData.resourceId,
        },
        mounted: async function mounted() {
        },
        methods: {
        },
        components: {
            RangeGraph,
        },
    });
};

window.pages = window.pages || {};
window.pages.resourcePage = {};
window.pages.resourcePage.init = init;
