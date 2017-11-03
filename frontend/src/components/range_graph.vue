<template>
  <div :id="graphId"></div>
</template>

<script>
    import moment from 'moment';
    import Plotly from 'plotly';
    import Vue from 'vue';
    import { get } from '../api';
    import { PAGE_TYPE_CONTENT, PAGE_TYPE_COMMUNICATION, PAGE_TYPE_ASSESSMENT } from '../consts';

    export default {
        props: {
            graphId: {
                type: String,
                required: true,
            },
            courseId: {
                type: Number,
                required: true,
            },
            courseStart: {
                type: String,
                required: true,
            },
            numWeeks: {
                type: Number,
                required: true,
            },
            studentId: {
                type: Number,
            },
            resourceId: {
                type: Number,
            },
            showType: {
                type: String,
            },
        },
    mounted() {
        let params = {};
        if (this.studentId) {
            params['student_id'] = this.studentId;
        }
        if (this.resourceId) {
            params['resource_id'] = this.resourceId;
        }

        const vue = this;

        get(`${this.courseId}/course_page_visits`, params).then((coursePageVisits) => {

            let maxVisits = 0;
            const dates = [];
            const contentVisits = [];
            const communicationVisits = [];
            const assessmentVisits = [];
            const singleEventsData = [];
            const submissionEventsData = [];
            const singleEventsText = [];
            const submissionEventsText = [];

            // Initial loop through data for page views
            _.forEach(coursePageVisits, function(visit) {
                dates.push(visit.day);
                contentVisits.push(visit.contentVisits);
                communicationVisits.push(visit.communicationVisits);
                assessmentVisits.push(visit.assessmentVisits);
                if (visit.contentVisits > maxVisits) {
                    maxVisits = visit.contentVisits;
                }
                if (visit.communicationVisits > maxVisits) {
                    maxVisits = visit.communicationVisits;
                }
                if (visit.assessmentVisits > maxVisits) {
                    maxVisits = visit.assessmentVisits;
                }
            });

            // Second loop to build events data
            _.forEach(coursePageVisits, function(visit) {
                if (visit.singleEvents.length) {
                    singleEventsData.push(maxVisits+1);
                    singleEventsText.push(_.join(visit.singleEvents, ', '));
                } else {
                    singleEventsData.push(null);
                    singleEventsText.push(null);
                }
                if (visit.submissionEvents.length) {
                    submissionEventsData.push(maxVisits+1);
                    submissionEventsText.push(_.join(visit.submissionEvents, ', '));
                } else {
                    submissionEventsData.push(null);
                    submissionEventsText.push(null);
                }
            });

            const graphData = [];

            if (!this.showType || this.showType === PAGE_TYPE_CONTENT) {
                graphData.push({
                    type: "scatter",
                    mode: "lines",
                    name: "Content",
                    x: dates,
                    y: contentVisits,
                });
            }

            if (!this.showType || this.showType === PAGE_TYPE_COMMUNICATION) {
                graphData.push({
                    type: "scatter",
                    mode: "lines",
                    name: "Communication",
                    x: dates,
                    y: communicationVisits,
                });
            }

            if (!this.showType || this.showType === PAGE_TYPE_ASSESSMENT) {
                graphData.push({
                    type: "scatter",
                    mode: "lines",
                    name: "Assessment",
                    x: dates,
                    y: assessmentVisits,
                });
            }

            graphData.push({
                type: "scatter",
                mode: "markers+text",
                name: "Single Events",
                x: dates,
                y: singleEventsData,
                text: singleEventsText,
                textposition: "top center",
            },
            {
                type: "scatter",
                mode: "markers+text",
                name: "Submission Events",
                x: dates,
                y: submissionEventsData,
                text: submissionEventsText,
                textposition: "top center",
            });

            // Make the range slider range a bit longer to show shaded sidebars
            const rangeStart = moment(vue.courseStart).add(-2, 'weeks').format('YYYY-MM-DD');
            const rangeEnd = moment(vue.courseStart).add(vue.numWeeks + 2, 'weeks').format('YYYY-MM-DD');

            const graphLayout = {
                xaxis: {
                    rangeselector: {
                        buttons: [
                            {
                                count: 1,
                                label: '1m',
                                step: 'month',
                                stepmode: 'backward'
                            },
                            {
                                count: 3,
                                label: '3m',
                                step: 'month',
                                stepmode: 'backward'
                            },
                            {
                                count: 6,
                                label: '6m',
                                step: 'month',
                                stepmode: 'backward'
                            },
                            {
                                count: 1,
                                label: 'YTD',
                                step: 'year',
                                stepmode: 'todate'
                            },
                            {
                                count: 1,
                                label: '1y',
                                step: 'year',
                                stepmode: 'backward'
                            },
                            {
                                label: 'All',
                                step: 'all',
                            },
                        ],
                        y: 1.1,
                    },
                    rangeslider: {
                        thickness: 0.3,
                        range: [rangeStart, rangeEnd],
                    },
                    type: 'date',
                },
                yaxis: {
                    range: [0, maxVisits + 2],
                }
            };

            const graphConfig = {
                modeBarButtonsToRemove: [
                    'sendDataToCloud',
                ],
            };

            Plotly.newPlot(
                vue.graphId,
                graphData,
                graphLayout,
                graphConfig,
            );
        });

    },
  };
</script>

<style lang="scss" module>

</style>
