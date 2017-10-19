import datetime
from factory import fuzzy
import json
import random

from django.test.testcases import TestCase
from django.urls.base import reverse
from django.utils.timezone import get_current_timezone

from rest_framework.test import APIClient
from rest_framework.status import HTTP_200_OK

from dashboard.tests.factories import LecturerFactory
from dashboard.tests.factories import CourseOfferingFactory
from dashboard.tests.factories import CourseRepeatingEventFactory
from olap.models import SubmissionAttempt
from olap.tests.factories import LMSUserFactory
from olap.tests.factories import PageFactory
from olap.tests.factories import PageVisitFactory
from olap.tests.factories import SubmissionAttemptFactory
from olap.tests.factories import SummaryPostFactory

# TODO: Test for permissions checks:
#  - Access to a course that the user doesn't own fails.
#  - Access to a course the user owns, but a repeating event the user doesn't, fails.

class APITestsBase(TestCase):
    def setUp(self):
        self.our_tz = get_current_timezone()
        self.user = LecturerFactory(password='12345')
        self.course_offering = CourseOfferingFactory()
        self.course_offering.owners.add(self.user)
        self.lms_user = LMSUserFactory(course_offering=self.course_offering)

        self.client = APIClient()
        login = self.client.login(username=self.user.email, password='12345')

    def get_dt_in_courseoffering_window(self):
        dt_range = (self.course_offering.start_datetime, self.course_offering.start_datetime + datetime.timedelta(weeks=self.course_offering.no_weeks))
        return fuzzy.FuzzyDateTime(*dt_range).fuzz()

class APICommunicationAccessesTests(APITestsBase):
    def test_accesses_one_page(self):
        self.api_url = reverse('olap:communication_accesses', kwargs={'course_id': self.course_offering.id})
        page = PageFactory(course_offering=self.course_offering, content_type='course/x-bb-collabsession')
        # For this one page, generate one visit per week for the duration of the course
        for week_no in range(self.course_offering.no_weeks):
            week_start_dt = self.course_offering.start_datetime + datetime.timedelta(weeks=week_no)
            week_end_dt = week_start_dt + datetime.timedelta(days=7)
            visit_dt = fuzzy.FuzzyDateTime(week_start_dt, week_end_dt)
            visit = PageVisitFactory(page=page, module='course/x-bb-collabsession', lms_user=self.lms_user, visited_at=visit_dt)

        # Call the API endpoint
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        totals = [1] * self.course_offering.no_weeks # One visit per week
        totals.append(self.course_offering.no_weeks) # Add a final number for the total visits
        expected = {
            'pageSet': [
                {
                    # These keys aren't getting camel cased.  No idea why.
                    'id': page.id,
                    'title': page.title,
                    'content_type': page.content_type,
                    'weeks': [1] * self.course_offering.no_weeks, # One visit per week
                    'total': self.course_offering.no_weeks, # One visit per week
                    'percent': 100.0,
               },
            ],
            'totalsByWeek': totals,
        }
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)

    def test_accesses_shedload_of_pages(self):
        self.api_url = reverse('olap:communication_accesses', kwargs={'course_id': self.course_offering.id})
        NR_PAGES = 5
        NR_PAGEVISITS = 100
        all_pages = PageFactory.create_batch(NR_PAGES, course_offering=self.course_offering, content_type='course/x-bb-collabsession')
        # Pick a random page, and create a visit to that page.
        for visit in range(NR_PAGEVISITS):
            end_dt = self.course_offering.start_datetime + datetime.timedelta(weeks=self.course_offering.no_weeks)
            random_visit_dt = fuzzy.FuzzyDateTime(self.course_offering.start_datetime, end_dt)
            random_page = all_pages[random.randint(0, NR_PAGES - 1)]
            visit = PageVisitFactory(page=random_page, module='course/x-bb-collabsession', lms_user=self.lms_user, visited_at=random_visit_dt)

        # Call the API endpoint
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        response_dict = json.loads(response.content.decode('utf-8'))
        # FIXME: This could be greatly expanded to check the numbers in the response.
        self.assertEqual(len(response_dict), 2)
        self.assertIn('pageSet', response_dict)
        self.assertIn('totalsByWeek', response_dict)
        page_set = response_dict['pageSet']
        self.assertEqual(len(page_set), NR_PAGES)
        # Could add more tests here.  Is it worth it?


class APICommunicationPostsTests(APITestsBase):
    def test_posts_one_page(self):
        api_url = reverse('olap:communication_posts', kwargs={'course_id': self.course_offering.id})
        page = PageFactory(course_offering=self.course_offering, content_type='resource/x-bb-discussionboard')
        # For this one page, generate one post per week for the duration of the course
        for week_no in range(self.course_offering.no_weeks):
            week_start_dt = self.course_offering.start_datetime + datetime.timedelta(weeks=week_no)
            week_end_dt = week_start_dt + datetime.timedelta(days=7)
            post_event_dt = fuzzy.FuzzyDateTime(week_start_dt, week_end_dt)
            post_event = SummaryPostFactory(page=page, lms_user=self.lms_user, posted_at=post_event_dt)

        # Call the API endpoint
        response = self.client.get(api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        totals = [1] * self.course_offering.no_weeks # One visit per week
        totals.append(self.course_offering.no_weeks) # Add a final number for the total visits
        expected = {
            'pageSet': [
                {
                    'id': page.id,
                    'title': page.title,
                    'content_type': page.content_type,
                    'weeks': [1] * self.course_offering.no_weeks, # One visit per week
                    'total': self.course_offering.no_weeks, # One visit per week
                    'percent': 100.0,
               },
            ],
            'totalsByWeek': totals,
        }
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)


class APICommunicationStudentsTests(APITestsBase):
    def test_students_one_page(self):
        course_offering = CourseOfferingFactory(start_date=self.course_offering.start_date, no_weeks=2)
        course_offering.owners.add(self.user)
        self.api_url = reverse('olap:communication_students', kwargs={'course_id': course_offering.id})
        # Two pages, two users
        page1 = PageFactory(course_offering=course_offering, content_type='resource/x-bb-discussionboard')
        page2 = PageFactory(course_offering=course_offering, content_type='resource/x-bb-discussionboard')
        lms_user1 = LMSUserFactory(course_offering=course_offering)
        lms_user2 = LMSUserFactory(course_offering=course_offering)

        # 2 pages and 2 weeks gives a 2x2 grid.
        # Top left: 1xU1, 2xU2
        visit_dt = self.course_offering.start_datetime + datetime.timedelta(days=3)
        visit = PageVisitFactory(page=page1, lms_user=lms_user1, visited_at=visit_dt)
        visit = PageVisitFactory(page=page1, lms_user=lms_user2, visited_at=visit_dt)
        visit = PageVisitFactory(page=page2, lms_user=lms_user2, visited_at=visit_dt)
        # Top right: 1xU1
        visit_dt = self.course_offering.start_datetime + datetime.timedelta(days=10)
        visit = PageVisitFactory(page=page1, lms_user=lms_user1, visited_at=visit_dt)
        # Bottom left: 1xU2
        visit_dt = self.course_offering.start_datetime + datetime.timedelta(days=5)
        visit = PageVisitFactory(page=page2, lms_user=lms_user2, visited_at=visit_dt)
        # Nothing in bottom right

        # Call the API endpoint
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = {
            'pageSet': [
                {
                    'id': page1.id,
                    'title': page1.title,
                    'content_type': page1.content_type,
                    'weeks': [2, 1],
                    'total': 2,
                    'percent': 100.0, # 100% of users interacted with this page
               },
                {
                    'id': page2.id,
                    'title': page2.title,
                    'content_type': page2.content_type,
                    'weeks': [1, 0],
                    'total': 1,
                    'percent': 50.0, # 50% of users (u2) interacted with this page
                },
            ],
            'totalsByWeek': [
                2, # 2 users (u1, u2) viewed the two pages in week 1
                1, # 1 users viewed the two pages in week 2
                2,
            ],
        }
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)


class APICommunicationEventsTests(APITestsBase):
    def events_setUp(self):
        self.course_offering_start = datetime.datetime(2016, 2, 1, 8, 0, 10, tzinfo=self.our_tz) # Mon
        assert self.course_offering_start.weekday() == 0 # Date chosen to be a monday.  Test won't work otherwise.

        course_offering = CourseOfferingFactory(start_date=self.course_offering_start, no_weeks=2)
        course_offering.owners.add(self.user)
        self.page = PageFactory(course_offering=course_offering, content_type='resource/x-bb-discussionboard')

        visit_dt = self.course_offering_start + datetime.timedelta(days=3) # Thu
        visit = PageVisitFactory(page=self.page, lms_user=self.lms_user, visited_at=visit_dt)

        # Default to Monday, but each test will change this to each side of the page visit
        self.repeating_event = CourseRepeatingEventFactory(course_offering=course_offering, start_week=1, end_week=2, day_of_week=0)

        self.api_url = reverse('olap:communication_events', kwargs={'course_id': course_offering.id, 'event_id': self.repeating_event.id})

    def test_events_one_page_view_before_event(self):
        self.events_setUp()
        self.repeating_event.day_of_week = 4 # Fri, visit is Thu
        self.repeating_event.save()

        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = [
            {
                'id': self.page.id,
                'title': self.page.title,
                'contentType': self.page.content_type,
                'weeks': [[1, 0], [0, 0]],
            }
        ]
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)

    def test_events_one_page_view_after_event(self):
        self.events_setUp()
        self.repeating_event.day_of_week = 2 # Wed, visit is Thu
        self.repeating_event.save()

        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = [
            {
                'id': self.page.id,
                'title': self.page.title,
                'contentType': self.page.content_type,
                'weeks': [[0, 1], [0, 0]],
            }
        ]
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)

    def test_events_one_page_view_on_day_of_event(self):
        self.events_setUp()
        # According to Slack discn 6-Oct, a page visit on the day of the event should be in the after bin.
        self.repeating_event.day_of_week = 3 # Thu, same day as visit
        self.repeating_event.save()

        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = [
            {
                'id': self.page.id,
                'title': self.page.title,
                'contentType': self.page.content_type,
                'weeks': [[0, 1], [0, 0]],
            }
        ]
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)

    def test_events_one_page_view_before_event_in_week1_one_page_view_after_event_in_week2(self):
        self.events_setUp()
        # At this moment, we have one visit on the Thursday of the first week.  This will make the visit before
        # the event (Friday)
        self.repeating_event.day_of_week = 4 # Every friday
        self.repeating_event.save()
        # Now create a second visit that's on the Saturday of week 2.  This will make the visit after the event.
        visit2_dt = self.course_offering_start + datetime.timedelta(weeks=1, days=5) # Sat
        visit2 = PageVisitFactory(page=self.page, lms_user=self.lms_user, visited_at=visit2_dt)

        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = [
            {
                'id': self.page.id,
                'title': self.page.title,
                'contentType': self.page.content_type,
                'weeks': [[1, 0], [0, 1]],
            }
        ]
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)

    def test_events_one_page_view_not_inside_event_window(self):
        self.events_setUp()

        self.repeating_event.day_of_week = 3 # Thu in week 1
        self.repeating_event.save()

        # Get the only visit to the page and move it to week three (event only runs for first two)
        visit = self.page.pagevisit_set.get()
        visit.visited_at += datetime.timedelta(weeks=3)
        visit.save()

        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = [
            {
                'id': self.page.id,
                'title': self.page.title,
                'contentType': self.page.content_type,
                'weeks': [[0, 0], [0, 0]],
            }
        ]
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)


class APIAssessmentsGradesTests(APITestsBase):
    def dont_test_three_students_three_assessments_simple(self):
        course_offering  = self.course_offering
        # Three students, three assessments, for 9 submission attempts (ie, no double-ups, none missing)
        students = LMSUserFactory.create_batch(3, course_offering=course_offering)
        assessments = PageFactory.create_batch(3, course_offering=course_offering, content_type='resource/x-turnitin-assignment')
        for student in students:
            for assessment in assessments:
                sa = SubmissionAttemptFactory(page=assessment, lms_user=student, attempted_at=self.get_dt_in_courseoffering_window())

        # Call the API endpoint
        api_url = reverse('olap:assessment_grades', kwargs={'course_id': self.course_offering.id})
        response = self.client.get(api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = {
            'users': list([user.id, user.full_name()] for user in students),
            'assessments': list([assessment.id, assessment.title] for assessment in assessments),
            'grades': [[float(sa.grade) for sa in SubmissionAttempt.objects.filter(lms_user=s)] for s in students]
        }

        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)

    def test_missing_assessment(self):
        course_offering  = self.course_offering
        # One student, two assessments.  Only the first has been attempted.
        assessments = PageFactory.create_batch(2, course_offering=course_offering, content_type='resource/x-turnitin-assignment')
        grade = 1.2345
        sa = SubmissionAttemptFactory(page=assessments[0], lms_user=self.lms_user, attempted_at=self.get_dt_in_courseoffering_window(), grade=grade)

        # Call the API endpoint
        api_url = reverse('olap:assessment_grades', kwargs={'course_id': self.course_offering.id})
        response = self.client.get(api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = {
            'users': [[self.lms_user.id, self.lms_user.full_name()]],
            'assessments': list([assessment.id, assessment.title] for assessment in assessments),
            'grades': [[grade, None]],
        }

    def test_only_saves_latest_submission(self):
        course_offering = self.course_offering
        # One student, one assessment.  There are two assessment submissions.
        assessment = PageFactory(course_offering=course_offering, content_type='resource/x-turnitin-assignment')
        # Make the first assessment
        grade_1 = 5.4321
        attempted_dt = self.get_dt_in_courseoffering_window()
        sa1 = SubmissionAttemptFactory(page=assessment, lms_user=self.lms_user, attempted_at=attempted_dt, grade=grade_1)
        # Make the second assessment
        grade_2 = 1.2345
        attempted_dt += datetime.timedelta(seconds=1)
        sa2 = SubmissionAttemptFactory(page=assessment, lms_user=self.lms_user, attempted_at=attempted_dt, grade=grade_2)

        # Call the API endpoint
        api_url = reverse('olap:assessment_grades', kwargs={'course_id': self.course_offering.id})
        response = self.client.get(api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        expected = {
            'users': [[self.lms_user.id, self.lms_user.full_name()]],
            'assessments': [[assessment.id, assessment.title]],
            'grades': [[grade_2]],
        }

        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)

    def dont_test_posts_one_page(self):
        self.api_url = reverse('olap:communication_posts', kwargs={'course_id': self.course_offering.id})
        page = PageFactory(course_offering=self.course_offering, content_type='resource/x-bb-discussionboard')
        # For this one page, generate one post per week for the duration of the course
        for week_no in range(self.course_offering.no_weeks):
            week_start_dt = self.course_offering.start_datetime + datetime.timedelta(weeks=week_no)
            week_end_dt = week_start_dt + datetime.timedelta(days=7)
            post_event_dt = fuzzy.FuzzyDateTime(week_start_dt, week_end_dt)
            post_event = SummaryPostFactory(page=page, lms_user=self.lms_user, posted_at=post_event_dt)

        # Call the API endpoint
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        totals = [1] * self.course_offering.no_weeks # One visit per week
        totals.append(self.course_offering.no_weeks) # Add a final number for the total visits
        expected = {
            'pageSet': [
                {
                    'id': page.id,
                    'title': page.title,
                    'content_type': page.content_type,
                    'weeks': [1] * self.course_offering.no_weeks, # One visit per week
                    'total': self.course_offering.no_weeks, # One visit per week
                    'percent': 100.0,
               },
            ],
            'totalsByWeek': totals,
        }
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict, expected)

