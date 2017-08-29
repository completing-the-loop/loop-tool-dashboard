import Vue from 'vue';
import $ from 'jquery';
import AsyncComputed from 'vue-async-computed';

import './styles/main.scss';

Vue.use(AsyncComputed);

Vue.directive('tooltip', (el, binding) => {
    $(el).attr('data-toggle', 'tooltip')
        .attr('data-placement', binding.arg)
        .attr('trigger', 'hover')
        .tooltip({ title: binding.value });
});
