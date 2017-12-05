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
        this.plotHistogram();
    },
    watch: {
        weekNum: function (val) {
            this.plotHistogram();
        },
    },
    methods: {
        plotHistogram() {
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
                if (studentPageVisits.length) {
                    maxVisits = studentPageVisits[studentPageVisits.length - 1].numVisits;
                }
                const binSize = Math.ceil(maxVisits / this.numBins);

                let zeroBin = 0;
                let binLabels, binData;
                if (binSize) {
                    binData = new Array(this.numBins).fill(0);
                    binLabels = new Array(this.numBins).fill('');
                    binLabels = _.map(binLabels, function(label, index) {
                        if (index) {
                            return `${(index * binSize) + 1} - ${(index + 1) * binSize}`;
                        } else {
                            return `<= ${binSize}`;
                        }
                    });

                    // Loop through the page visits and assign to bins
                    _.forEach(studentPageVisits, function (visit) {
                        if (visit.numVisits) {
                            const binIndex = Math.floor((visit.numVisits - 1) / binSize);
                            binData[binIndex] += 1;
                        } else {
                            zeroBin += 1;
                        }
                    });
                } else {
                    binLabels = ["> 0"];
                    binData = [0];
                    zeroBin = studentPageVisits.length;
                }

                binData.unshift(zeroBin);
                binLabels.unshift("None");

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
    },
  };
</script>

<style lang="scss" module>

</style>
