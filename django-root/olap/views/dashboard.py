import datetime
from datetime import timedelta

from django.db.models import Avg
from django.db.models import Count
from django.utils.timezone import get_current_timezone
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CourseOffering
from dashboard.models import CourseRepeatingEvent
from dashboard.models import CourseSingleEvent
from dashboard.models import CourseSubmissionEvent
from olap.models import LMSUser
from olap.models import Page
from olap.models import PageVisit
from olap.models import SubmissionAttempt
from olap.models import SummaryPost
from olap.serializers import DailyPageVisitsSerializer
from olap.serializers import TopAccessedContentSerializer
from olap.serializers import TopAssessmentAccessSerializer
from olap.serializers import TopCommunicationAccessSerializer
from olap.serializers import TopCourseUsersSerializer
from olap.serializers import WeeklyPageVisitsSerializer


class TopCourseUsersViewSet(ListAPIView):
    serializer_class = TopCourseUsersSerializer
    max_rows_to_return = 10

    def get_queryset(self):
        qs = LMSUser.objects.annotate(pageviews=Count("pagevisit")).filter(course_offering=self.request.course_offering).order_by('-pageviews')[0:self.max_rows_to_return]

        return qs


class TopAccessedContentView(ListAPIView):
    serializer_class = TopAccessedContentSerializer
    max_rows_to_return = 10

    def get_queryset(self):
        course_offering = self.request.course_offering
        # Was a week number specified? (week number is 1-based)
        week_num = self.kwargs.get('week_num')
        if week_num is not None:
            # Filter for pagevisits within the week
            range_start = course_offering.start_datetime + datetime.timedelta(weeks=int(week_num) - 1)
            range_end = range_start + datetime.timedelta(weeks=1)
        else:
            # Filter for pagevisits within the extent of the courseoffering
            range_start = course_offering.start_datetime
            range_end = range_start + datetime.timedelta(weeks=course_offering.no_weeks)
        dt_range = (range_start, range_end)

        # Get the page list.  pageviews can be done in the query.
        page_qs = Page.objects.filter(course_offering=course_offering, pagevisit__visited_at__range=dt_range).values('id', 'title', 'content_type').annotate(pageviews=Count("pagevisit")).order_by('-pageviews')[0:self.max_rows_to_return]

        # Now calculate the data for the userviews column by finding the number of distinct users to access each page in the time period.
        # FIXME: This isn't a great way to do it.  Would be good to do it as part of the query above, in a way that didn't involve iteration or sets.
        for page in page_qs:
            page['userviews'] = len(set(LMSUser.objects.filter(pagevisit__page=page['id'], pagevisit__visited_at__range=dt_range)))

        return page_qs


class TopCommunicationAccessView(ListAPIView):
    serializer_class = TopCommunicationAccessSerializer
    max_rows_to_return = 10

    def get_queryset(self):
        course_offering = self.request.course_offering
        # Was a week number specified? (week number is 1-based)
        week_num = self.kwargs.get('week_num')
        if week_num is not None:
            # Filter for pagevisits within the week
            range_start = course_offering.start_datetime + datetime.timedelta(weeks=int(week_num) - 1)
            range_end = range_start + datetime.timedelta(weeks=1)
        else:
            # Filter for pagevisits within the extent of the courseoffering
            range_start = course_offering.start_datetime
            range_end = range_start + datetime.timedelta(weeks=course_offering.no_weeks)
        dt_range = (range_start, range_end)

        # Get the page list.  If only we could do all this at the db level.
        page_qs = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.communication_types()).values('id', 'title', 'content_type')

        # Augment all the pages with how many page views related to that page for the window of interest.
        for page in page_qs:
            page['pageviews'] = PageVisit.objects.filter(page=page['id'], visited_at__range=dt_range).count()

        # Sort by number of page views and trim down to top 10 rows
        # WARNING: This is messing with the internals of the query set
        page_qs._result_cache = sorted(page_qs._result_cache, key=lambda p: p['pageviews'], reverse=True)[0:self.max_rows_to_return]

        # Now calculate the data for the userviews and posts columns.
        # FIXME: This isn't a great way to do it.  Would be good to do it as part of the query above, in a way that didn't involve iteration or sets.
        for page in page_qs:
            # The userviews value is the number of distinct users to access this page in the time period.
            page['userviews'] = LMSUser.objects.filter(pagevisit__page=page['id'], pagevisit__visited_at__range=dt_range).distinct().count()
            # The posts value is the number of posts to this page in the window of interest.
            page['posts'] = SummaryPost.objects.filter(page=page['id'], posted_at__range=dt_range).count()

        return page_qs


class TopAssessmentAccessView(ListAPIView):
    serializer_class = TopAssessmentAccessSerializer
    max_rows_to_return = 10

    def get_queryset(self):
        course_offering = self.request.course_offering
        # Was a week number specified? (week number is 1-based)
        week_num = self.kwargs.get('week_num')
        if week_num is not None:
            # Filter for assessment accesses within the week
            range_start = course_offering.start_datetime + datetime.timedelta(weeks=int(week_num) - 1)
            range_end = range_start + datetime.timedelta(weeks=1)
        else:
            # Filter for assessment accesses within the extent of the courseoffering
            range_start = course_offering.start_datetime
            range_end = range_start + datetime.timedelta(weeks=course_offering.no_weeks)
        dt_range = (range_start, range_end)

        # Get the page list.  If only we could do all this at the db level.
        page_qs = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.assessment_types()).values('id', 'title', 'content_type')

        # Augment all the pages with how many submission attempts related to that page for the window of interest.
        for page in page_qs:
            page['attempts'] = SubmissionAttempt.objects.filter(page=page['id'], attempted_at__range=dt_range).count()

        # Sort by number of submission attempts and trim down to top 10 rows
        # WARNING: This is messing with the internals of the query set
        page_qs._result_cache = sorted(page_qs._result_cache, key=lambda p: p['attempts'], reverse=True)[0:self.max_rows_to_return]

        # Now calculate the data for the userviews and average score columns.
        # FIXME: This isn't a great way to do it.  Would be good to do it as part of the query above, in a way that didn't involve iteration or sets.
        for page in page_qs:
            # The userviews value is the number of distinct users to make a submission attempt in the time period.
            page['userviews'] = LMSUser.objects.values('id').filter(submissionattempt__page=page['id'], submissionattempt__attempted_at__range=dt_range).distinct().count()
            # The average score is the average of scores for submission attempts in the time period.
            # FIXME: Check for average-related exceptions here.
            avg = SubmissionAttempt.objects.filter(page=page['id'], attempted_at__range=dt_range).aggregate(Avg('grade'))
            page['average_score'] = avg['grade__avg']

        return page_qs


class OverallPageVisitsView(APIView):
    def get(self, request, *args, **kwargs):
        # Setup list of days in course with initial values
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

        # Add the page visits to their corresponding entry
        for page_visit in PageVisit.objects.filter(page__course_offering=request.course_offering).values('visited_at', 'page__content_type'):
            visit_date = page_visit['visited_at'].astimezone(our_tz).date()
            if page_visit['page__content_type'] in CourseOffering.communication_types():
                day_dict[visit_date]['communication_visits'] += 1
            elif page_visit['page__content_type'] in CourseOffering.assessment_types():
                day_dict[visit_date]['assessment_visits']+= 1
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


class PerWeekPageVisitsView(APIView):
    def get(self, request, *args, **kwargs):

        week_num = kwargs.get('week_num')
        week_start = request.course_offering.start_datetime + datetime.timedelta(weeks=int(week_num) - 1)
        dt_range = (week_start, week_start + datetime.timedelta(weeks=1))
        our_tz = get_current_timezone()

        day_dict = {}
        for day_offset in range(7):
            day = (week_start + datetime.timedelta(days=day_offset)).date()
            day_dict[day] = {
                'day': day,
                'content_visits': 0,
                'communication_visits': 0,
                'assessment_visits': 0,
                'page_list': [],
                'repeating_events': [],
            }

        # Add the page visits to their corresponding entry
        for page_visit in PageVisit.objects.filter(page__course_offering=request.course_offering, visited_at__range=dt_range).values('page_id', 'visited_at', 'page__content_type'):
            visit_date = page_visit['visited_at'].astimezone(our_tz).date()
            day_dict[visit_date]['page_list'].append(page_visit['page_id'])
            if page_visit['page__content_type'] in CourseOffering.communication_types():
                day_dict[visit_date]['communication_visits'] += 1
            elif page_visit['page__content_type'] in CourseOffering.assessment_types():
                day_dict[visit_date]['assessment_visits']+= 1
            else:
                day_dict[visit_date]['content_visits'] += 1

        # Add the repeating events to their corresponding entry
        for repeating_event in CourseRepeatingEvent.objects.filter(course_offering=request.course_offering, start_week__lte=week_num, end_week__gte=week_num):
            repeat_event_date = week_start + datetime.timedelta(days=repeating_event.day_of_week)
            day_dict[repeat_event_date.date()]['repeating_events'].append(repeating_event.title)

        # Turn the list of pages visited for each day into a count of unique visits
        for day in day_dict:
            day_dict[day]['unique_visits'] = len(set(day_dict[day]['page_list']))
            del day_dict[day]['page_list']

        # Convert to array and serialize
        data = [v for v in day_dict.values()]
        data.sort(key=lambda day_data: day_data['day'])
        serializer = WeeklyPageVisitsSerializer(data, many=True)
        return Response(serializer.data)
