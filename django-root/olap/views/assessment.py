from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CourseOffering
from dashboard.models import CourseRepeatingEvent
from olap.models import LMSUser
from olap.models import Page
from olap.models import PageVisit
from olap.models import SubmissionAttempt
from olap.serializers import AssessmentUsersAndGradesSerializer
from olap.serializers import CourseEventSerializer
from olap.serializers import CoursePagesetAndTotalsSerializer

# Base class for AssessmentAccessesView.
# What the derived classes do is very similar - they look at events.
# This class could probably be folded in with olap.views.communications.CommunicationGenericView
class AssessmentGenericView(APIView):
    def get_event_queryset(self, page_id):
        raise NotImplementedError

    def get_event_time(self, event):
        raise NotImplementedError

    def get(self, request, format=None):
        course_offering = self.request.course_offering
        course_start_dt = course_offering.start_datetime

        events_by_week_for_all_pages = [0] * course_offering.no_weeks
        page_queryset = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.assessment_types()).values('id', 'title', 'content_type')
        total_events = 0
        for page in page_queryset:
            events_for_this_page = self.get_event_queryset(page['id'])
            events_by_week_for_this_page = [0] * course_offering.no_weeks
            total_events += events_for_this_page.count()
            for event in events_for_this_page:
                # Calculate the time since start of course for this event.  From this we can calculate the week.
                # (Note, it's ok for courses not to start on Monday.  In this case, the boundary of the course week won't
                # be the same as the inter-week boundary).
                td = self.get_event_time(event) - course_start_dt
                week = td.days // 7  # Integer division, the first week after the course starts is week 0.
                try:
                    # try is here to catch invalid week indexes caused by events outside of the course offering.
                    events_by_week_for_this_page[week] += 1
                    events_by_week_for_all_pages[week] += 1
                except IndexError:
                    pass
            page['weeks'] = events_by_week_for_this_page
            page['total'] = sum(events_by_week_for_this_page) # Add along the row.

        # Total things for all pages and weeks.  Will appear in bottom right corner.
        events_by_week_for_all_pages.append(total_events)
        # Calculate percentages.
        for page in page_queryset:
            page['percent'] = (Decimal(page['total'] * 100 / total_events) if total_events else 0)

        results = {
            'page_set': page_queryset,
            'totals_by_week': events_by_week_for_all_pages,
        }

        serializer = CoursePagesetAndTotalsSerializer(data=results)
        # If we pass data to the serializer, we need to call .is_valid() before it's available in .data
        serializer.is_valid()
        sd = serializer.data

        return Response(sd)


class AssessmentAccessesView(AssessmentGenericView):
    def get_event_queryset(self, page_id):
        return SubmissionAttempt.objects.filter(page_id=page_id)

    def get_event_time(self, event):
        return event.attempted_at


class AssessmentGradesView(APIView):
    def get(self, request, format=None):
        course_offering = self.request.course_offering

        users_set = LMSUser.objects.filter(course_offering=course_offering).order_by('lms_user_id') # TODO: values()
        users_out = []
        assessments_set = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.assessment_types()).order_by('pk').values('id', 'title')
        page_ids = tuple(a['id'] for a in assessments_set)
        for user in users_set:
            most_recent_attempts = {} # Dict of attempts for this student, keyed by assessment id
            # Find all the attempts for this student
            attempts = SubmissionAttempt.objects.filter(lms_user__id=user.id, page__in=page_ids)
            # Iterate over the attempts, recording the most recent attempt in the dict
            for attempt in attempts:
                page_id = attempt.page_id
                # If we don't have an attempt for this assessment, or this is a more recent attempt, store it.
                if page_id not in most_recent_attempts or attempt.attempted_at > most_recent_attempts[page_id].attempted_at:
                    most_recent_attempts[page_id] = attempt
            # Take the dict of most recent attempts, and extract the grades.  No attempt gives a None grade.
            grades = {str(k): {'pk': k, 'grade': v.grade} for k, v in most_recent_attempts.items()}
            users_out.append({'pk': user.id, 'name': user.full_name(), 'grades': grades})

        results = {
            'assessments': [{'pk': assessment['id'], 'title': assessment['title']} for assessment in assessments_set],
            'users': users_out,
        }

        serializer = AssessmentUsersAndGradesSerializer(data=results)
        sd = serializer.initial_data

        return Response(sd)


class AssessmentStudentsView(APIView):
    def get(self, request, format=None):
        course_offering = self.request.course_offering
        course_start_dt = course_offering.start_datetime

        students_by_week_for_all_pages = [set() for i in range(course_offering.no_weeks)]
        page_queryset = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.assessment_types()).values('id', 'title', 'content_type')
        for page in page_queryset:
            page_visits_for_this_page = PageVisit.objects.filter(page_id=page['id'])
            students_by_week_for_this_page = [set() for i in range(course_offering.no_weeks)]
            for visit in page_visits_for_this_page:
                # Calculate the time since start of course for this page visit.  From this we can calculate the week.
                # (Note, it's ok for courses not to start on Monday.  In this case, the boundary of the course week won't
                # be the same as the isoweek boundary).
                td = visit.visited_at - course_start_dt
                week = td.days // 7  # Integer division, the first week after the course starts is week 0.
                try:
                    # try is here to catch invalid week indexes caused by events outside of the course offering.
                    students_by_week_for_this_page[week].add(visit.lms_user.pk)
                    students_by_week_for_all_pages[week].add(visit.lms_user.pk)
                except IndexError:
                    pass
            # At this point we have a list of sets of students for the page.  Take the union of all the sets to find
            # the set of students who visited this page at any time over the duration of the course offering.
            set_of_students_for_this_page = set.union(*students_by_week_for_this_page)
            # For each week bin, convert the set of students for that weekinto a count.
            students_by_week_for_this_page = list(len(students) for students in students_by_week_for_this_page)
            page['weeks'] = students_by_week_for_this_page
            page['total'] = len(set_of_students_for_this_page)

        grand_total_uniques = len(set.union(*students_by_week_for_all_pages))
        # For each week bin, convert the set of students for that weekinto a count.
        students_by_week_for_all_pages = list(len(students) for students in students_by_week_for_all_pages)
        # Total page students for all pages and weeks.  Will appear in bottom right corner.
        students_by_week_for_all_pages.append(grand_total_uniques)

        # Calculate percentages.
        for page in page_queryset:
            page['percent'] = (Decimal(page['total'] * 100 / grand_total_uniques) if grand_total_uniques else 0)

        results = {
            'page_set': list(page_queryset),
            'totals_by_week': students_by_week_for_all_pages,
        }

        serializer = CoursePagesetAndTotalsSerializer(data=results)
        sd = serializer.initial_data

        return Response(sd)


class AssessmentEventsView(APIView):
    def get(self, request, event_id, format=None):
        course_offering = self.request.course_offering
        repeating_event = get_object_or_404(CourseRepeatingEvent, pk=event_id, course_offering=course_offering)

        our_tz = get_current_timezone()
        course_start_dt = course_offering.start_datetime

        page_queryset = Page.objects.filter(course_offering=course_offering, content_type__in=CourseOffering.assessment_types()).values('id', 'title', 'content_type')
        for page in page_queryset:
            page_visits_for_this_page = PageVisit.objects.filter(page_id=page['id'])
            visit_pairs_by_week = [[0, 0] for i in range(course_offering.no_weeks)]
            for visit in page_visits_for_this_page:
                # Calculate the time since start of course for this page visit.  From this we can calculate the week.
                # (Note, it's ok for courses not to start on Monday.  In this case, the boundary of the course week won't
                # be the same as the isoweek boundary).
                td = visit.visited_at - course_start_dt
                week = td.days // 7  # Integer division, the first week after the course starts is week 0.
                visit_date_in_local_tz = visit.visited_at.astimezone(our_tz).date()
                day_of_week_of_visit = visit_date_in_local_tz.weekday()
                try:  # Is the date of the visit within the range defined by the course offering?
                    if day_of_week_of_visit < repeating_event.day_of_week:
                        visit_pairs_by_week[week][0] += 1
                    else:
                        visit_pairs_by_week[week][1] += 1
                except IndexError:
                    pass
            page['weeks'] = visit_pairs_by_week

        serializer = CourseEventSerializer(page_queryset, many=True)
        sd = serializer.data

        return Response(sd)
