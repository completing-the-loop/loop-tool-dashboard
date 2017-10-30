import Vue from 'vue';
import $ from 'jquery';
import AsyncComputed from 'vue-async-computed/dist/vue-async-computed';

import './styles/main.scss';

Vue.use(AsyncComputed);

import datePicker from 'vue-bootstrap-datetimepicker';
import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css';
Vue.use(datePicker);

Vue.directive('tooltip', (el, binding) => {
    $(el).attr('data-toggle', 'tooltip')
        .attr('data-placement', binding.arg)
        .attr('trigger', 'hover')
        .tooltip({ title: binding.value });
});
