from datetime import timedelta

from django.db.models import Count
from django.utils.timezone import get_current_timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CourseOffering
from dashboard.models import CourseSingleEvent
from dashboard.models import CourseSubmissionEvent
from olap.models import PageVisit
from olap.serializers import DailyPageVisitsSerializer
from olap.serializers import StudentPageVisitsHistogramSerializer


class CoursePageVisitsView(APIView):
    def get(self, request, *args, **kwargs):
        # Setup list of days in course with initial values
        student_id = request.GET.get('student_id')
        resource_id = request.GET.get('resource_id')

        day_dict = {}
        our_tz = get_current_timezone()
        course_span = request.course_offering.end_date - request.course_offering.start_date
        for day_offset in range(course_span.days + 1):
            day = request.course_offering.start_date + timedelta(days=day_offset)
            day_dict[day] = {
                'day': day,
                'content_visits': 0,
                'communication_visits': 0,
                'assessment_visits': 0,
                'single_events': [],
                'submission_events': [],
            }

        # Get page visits optionally filtered by student and page
        page_visit_qs = PageVisit.objects.filter(page__course_offering=request.course_offering)
        if student_id:
            page_visit_qs = page_visit_qs.filter(lms_user_id=student_id)
        if resource_id:
            page_visit_qs = page_visit_qs.filter(page_id=resource_id)

        # Add the page visits to their corresponding entry
        for page_visit in page_visit_qs.values('visited_at', 'page__content_type'):
            visit_date = page_visit['visited_at'].astimezone(our_tz).date()
            if page_visit['page__content_type'] in CourseOffering.communication_types():
                day_dict[visit_date]['communication_visits'] += 1
            elif page_visit['page__content_type'] in CourseOffering.assessment_types():
                day_dict[visit_date]['assessment_visits'] += 1
            else:
                day_dict[visit_date]['content_visits'] += 1

        # Add the single and submission events to their corresponding entry
        for single_event in CourseSingleEvent.objects.filter(course_offering=request.course_offering):
            day_dict[single_event.event_date.date()]['single_events'].append(single_event.title)

        for submission_event in CourseSubmissionEvent.objects.filter(course_offering=request.course_offering):
            day_dict[submission_event.start_date.date()]['submission_events'].append("{} (start)".format(submission_event.title))
            day_dict[submission_event.end_date.date()]['submission_events'].append("{} (end)".format(submission_event.title))

        # Convert to array and serialize
        data = [v for v in day_dict.values()]
        data.sort(key=lambda day_data: day_data['day'])
        serializer = DailyPageVisitsSerializer(data, many=True)
        return Response(serializer.data)


class StudentPageVisitsView(APIView):
    def get(self, request, *args, **kwargs):
        # Setup list of days in course with initial values
        week_num = request.GET.get('week_num')
        resource_id = request.GET.get('resource_id')

        # Filter the list of page visits
        page_visit_qs = PageVisit.objects.filter(page__course_offering=request.course_offering)
        if resource_id:
            page_visit_qs = page_visit_qs.filter(page_id=resource_id)
        if week_num:
            range_start = request.course_offering.start_datetime + timedelta(weeks=int(week_num) - 1)
            range_end = range_start + timedelta(weeks=1)
            page_visit_qs = page_visit_qs.filter(pagevisit__visited_at__range=(range_start, range_end))

        # Count the filtered page visits grouped by LMSUser
        page_visit_qs = page_visit_qs.values('lms_user_id').annotate(num_visits=Count('lms_user_id'))

        serializer = StudentPageVisitsHistogramSerializer(page_visit_qs, many=True)
        return Response(serializer.data)
