import Vue from 'vue';

const init = async (
    courseId,
) => {
    new Vue({
        el: '#course-dashboard',
        data: {
            courseId,
        },
        mounted: async function mounted() {
            // this.loadSubClassifications(false);
        },
        methods: {
            // async loadSubClassifications(reset = true) {
            //     if (reset) {
            //         this.subClassificationId = null;
            //     }
            //
            //     if (!this.classificationId) {
            //         this.subClassifications = [];
            //         return;
            //     }
            //
            //     const classification = await get(`job-classifications/${this.classificationId}`);
            //     this.subClassifications = [{ id: null, name: '---------' }, ...classification.subClassifications];
            // },
            // async getTeamNames(value) {
            //     return get('campaigns/team_names/', { q: value });
            // },
        },
    });
};

window.pages = window.pages || {};
window.pages.dashboard = {};
window.pages.dashboard.init = init;
