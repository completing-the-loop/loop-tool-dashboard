import Vue from 'vue';

const init = async (
    startDate,
    endDate,
    inputFormat,
) => {
    new Vue({
        el: '#course-submission-event-form',
        data: {
            startDate: startDate,
            endDate: endDate,
            config: {
                format: inputFormat,
                showClear: true,
                showTodayButton: true,
            },
        },
    });
};

window.pages = window.pages || {};
window.pages.courseSubmissionEventForm = {};
window.pages.courseSubmissionEventForm.init = init;
