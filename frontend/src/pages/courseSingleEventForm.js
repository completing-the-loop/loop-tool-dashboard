import Vue from 'vue';

const init = async (
    eventDate,
    inputFormat,
) => {
    new Vue({
        el: '#course-single-event-form',
        data: {
            eventDate: eventDate,
            config: {
                format: inputFormat,
                showClear: true,
                showTodayButton: true,
            },
        },
    });
};

window.pages = window.pages || {};
window.pages.courseSingleEventForm = {};
window.pages.courseSingleEventForm.init = init;
