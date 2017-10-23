from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils.timezone import get_current_timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CourseRepeatingEvent
from olap.models import LMSUser
from olap.models import PageVisit
from olap.serializers import StudentsetAndTotalsSerializer
from olap.serializers import StudentsetAndHighestSerializer


class StudentsAccessesView(APIView):
    def get(self, request, format=None):
        course_offering = self.request.course_offering
        course_start_dt = course_offering.start_datetime

        pagevisits_by_week_for_all_students = [0] * course_offering.no_weeks
        student_queryset = LMSUser.objects.filter(course_offering=course_offering)
        student_list = [{'id': s.id, 'fullname': s.full_name()} for s in student_queryset]
        total_pagevisits = 0
        highest_cell_value = None
        for student in student_list:
            pagevisits_for_this_student = PageVisit.objects.filter(lms_user_id=student['id'])
            pagevisits_by_week_for_this_page = [0] * course_offering.no_weeks
            total_pagevisits += pagevisits_for_this_student.count()
            for pagevisit in pagevisits_for_this_student:
                # Calculate the time since start of course for this pagevisit.  From this we can calculate the week.
                # (Note, it's ok for courses not to start on Monday.  In this case, the boundary of the course week won't
                # be the same as the inter-week boundary).
                td = pagevisit.visited_at - course_start_dt
                week = td.days // 7  # Integer division, the first week after the course starts is week 0.
                try:
                    # try is here to catch invalid week indexes caused by pagevisits outside of the course offering.
                    pagevisits_by_week_for_this_page[week] += 1
                    pagevisits_by_week_for_all_students[week] += 1
                except IndexError:
                    pass
            student['weeks'] = pagevisits_by_week_for_this_page
            student['total'] = sum(pagevisits_by_week_for_this_page) # Add along the row.
            highest_cell_for_this_student = max(pagevisits_by_week_for_this_page)
            try:
                highest_cell_value = max(highest_cell_value, highest_cell_for_this_student)
            except TypeError:
                # This happens if it's the first row and highest_cell_value wasn't set.
                highest_cell_value = highest_cell_for_this_student

        # Total things for all pages and weeks.  Will appear in bottom right corner.
        pagevisits_by_week_for_all_students.append(total_pagevisits)
        # Calculate percentages.
        for student in student_list:
            student['percent'] = (Decimal(student['total'] * 100 / total_pagevisits) if total_pagevisits else 0)

        results = {
            'student_set': student_list,
            'totals_by_week': pagevisits_by_week_for_all_students,
            'highest_cell_value': highest_cell_value,
        }

        serializer = StudentsetAndTotalsSerializer(data=results)
        sd = serializer.initial_data

        return Response(sd)


class StudentsEventsView(APIView):
    def get(self, request, event_id, format=None):
        course_offering = self.request.course_offering
        repeating_event = get_object_or_404(CourseRepeatingEvent, pk=event_id, course_offering=course_offering)

        our_tz = get_current_timezone()
        course_start_dt = course_offering.start_datetime

        student_queryset = LMSUser.objects.filter(course_offering=course_offering)
        student_list = [{'id': s.id, 'fullname': s.full_name()} for s in student_queryset]
        highest_cell_value = None
        for student in student_list:
            pagevisits_for_this_student = PageVisit.objects.filter(lms_user_id=student['id'])
            pagevisit_pairs_by_week = [[0, 0] for i in range(course_offering.no_weeks)]
            for pagevisit in pagevisits_for_this_student:
                # Calculate the time since start of course for this pagevisit.  From this we can calculate the week.
                # (Note, it's ok for courses not to start on Monday.  In this case, the boundary of the course week won't
                # be the same as the inter-week boundary).
                td = pagevisit.visited_at - course_start_dt
                week = td.days // 7  # Integer division, the first week after the course starts is week 0.
                pagevisit_date_in_local_tz = pagevisit.visited_at.astimezone(our_tz).date()
                day_of_week_of_pagevisit = pagevisit_date_in_local_tz.weekday()
                try:  # Is the date of the pagevisit within the range defined by the course offering?
                    if day_of_week_of_pagevisit < repeating_event.day_of_week:
                        pagevisit_pairs_by_week[week][0] += 1
                    else:
                        pagevisit_pairs_by_week[week][1] += 1
                except IndexError:
                    pass
            student['weeks'] = pagevisit_pairs_by_week
            highest_cell_for_this_student = max((sum(pv) for pv in pagevisit_pairs_by_week))
            try:
                highest_cell_value = max(highest_cell_value, highest_cell_for_this_student)
            except TypeError:
                # This happens if it's the first row and highest_cell_value wasn't set.
                highest_cell_value = highest_cell_for_this_student

        results = {
            'student_set': student_list,
            'highest_cell_value': highest_cell_value,
        }

        serializer = StudentsetAndHighestSerializer(data=results)
        sd = serializer.initial_data

        return Response(sd)
