import json

from django.conf import settings

from olap.models import Page


def constants(request):
    constants_json = json.dumps({
        'BASE_URL': request.build_absolute_uri('/'),
        'BASE_API_URL': request.build_absolute_uri('/api/'),
        'PAGE_INDENT_PIXELS': 19,  # Indent applied per level for tree grid on LMS page lists
        'PAGE_MIN_PIE_GRAPH_PIXELS': 10,
        'PAGE_MAX_PIE_GRAPH_PIXELS': 100,
        'PAGE_PIE_CHART_BEFORE_COLOR': 'blue',
        'PAGE_PIE_CHART_AFTER_COLOR': 'red',
        'PAGE_TYPE_CONTENT': Page.PAGE_TYPE_CONTENT,
        'PAGE_TYPE_COMMUNICATION': Page.PAGE_TYPE_COMMUNICATION,
        'PAGE_TYPE_ASSESSMENT': Page.PAGE_TYPE_ASSESSMENT,
        'RESOURCE_NUM_HISTOGRAM_BINS': settings.RESOURCE_NUM_HISTOGRAM_BINS,
    })

    return {'CONSTANTS': constants_json}
