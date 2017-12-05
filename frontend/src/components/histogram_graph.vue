<template>
  <div :id="graphId"></div>
</template>

<script>
    import moment from 'moment';
    import Plotly from 'plotly';
    import Vue from 'vue';
    import { get } from '../api';

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
            numBins: {
                type: Number,
                required: true,
            },
            weekNum: {
                type: Number,
            },
            resourceId: {
                type: Number,
            },
        },
    mounted() {
        let params = {};
        if (this.weekNum) {
            params['week_num'] = this.weekNum;
        }
        if (this.resourceId) {
            params['resource_id'] = this.resourceId;
        }

        get(`${this.courseId}/student_page_visits`, params).then((studentPageVisits) => {
            // Calculate the max visits and bin size
            let maxVisits = 0;
            if (studentPageVisits) {
                maxVisits = studentPageVisits[studentPageVisits.length - 1].numVisits;
            }
            const binSize = maxVisits / this.numBins;

            const binData = new Array(this.numBins).fill(0);
            let binLabels = new Array(this.numBins).fill('');
            binLabels = _.map(binLabels, function(label, index) {
                if (index) {
                    return `${(index * binSize) + 1} - ${(index + 1) * binSize}`;
                } else {
                    return `<= ${binSize}`;
                }
            });

            if (binSize) {
                // Loop through the page visits and assign to bins
                _.forEach(studentPageVisits, function (visit) {
                    const binIndex = Math.floor((visit.numVisits - 1) / binSize);
                    binData[binIndex] += 1;
                });
            }

            const graphData = [
                {
                  x: binLabels,
                  y: binData,
                  type: 'bar'
                }
            ];
            const graphLayout = {};
            const graphConfig = {
                modeBarButtonsToRemove: [
                    'sendDataToCloud',
                ],
            };

            Plotly.newPlot(
                this.graphId,
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
