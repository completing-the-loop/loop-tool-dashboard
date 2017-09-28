import datetime
from factory import fuzzy
import json
import random

from django.test.testcases import TestCase
from django.urls.base import reverse
from django.utils.timezone import get_current_timezone
from django.utils.timezone import make_aware

from rest_framework.test import APIClient
from rest_framework.status import HTTP_200_OK

from dashboard.tests.factories import LecturerFactory
from olap.models import PageVisit
from olap.tests.factories import CourseOfferingFactory
from olap.tests.factories import LMSUserFactory
from olap.tests.factories import PageFactory
from olap.tests.factories import PageVisitFactory

class APICommunicationAccessesTests(TestCase):
    def setUp(self):
        self.our_tz = get_current_timezone()
        self.user = LecturerFactory(password='12345')
        self.lms_user = LMSUserFactory()
        self.course_offering = CourseOfferingFactory()
        self.course_offering.owners.add(self.user)

        # Turn the course start date (which we presume is in the local timezone) into a tz aware datetime
        self.course_start_dt = make_aware(datetime.datetime.combine(self.course_offering.start_date, datetime.time()), timezone=self.our_tz)

        self.client = APIClient()
        login = self.client.login(username=self.user.email, password='12345')
        self.api_url = reverse('olap:communication_accesses', kwargs={'course_id': self.course_offering.id})

    def test_one_page(self):
        page = PageFactory(course_offering=self.course_offering, content_type='course/x-bb-collabsession')
        # For this one page, generate one visit per week for the duration of the course
        for week_no in range(self.course_offering.no_weeks):
            week_start_dt = self.course_start_dt + datetime.timedelta(weeks=week_no)
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

    def test_shedload_of_pages(self):
        NR_PAGES = 5
        NR_PAGEVISITS = 100
        all_pages = PageFactory.create_batch(NR_PAGES, course_offering=self.course_offering, content_type='course/x-bb-collabsession')
        for visit in range(NR_PAGEVISITS):
            end_dt = self.course_start_dt + datetime.timedelta(weeks=self.course_offering.no_weeks)
            random_visit_dt = fuzzy.FuzzyDateTime(self.course_start_dt, end_dt)
            random_page = all_pages[random.randint(0, NR_PAGES - 1)]
            visit = PageVisitFactory(page=random_page, module='course/x-bb-collabsession', lms_user=self.lms_user,
                                     visited_at=random_visit_dt)

        # Call the API endpoint
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response_dict), 2)
        self.assertIn('pageSet', response_dict)
        self.assertIn('totalsByWeek', response_dict)
        page_set = response_dict['pageSet']
        self.assertEqual(len(page_set), NR_PAGES)
        # Could add more tests here.  Is it worth it?
