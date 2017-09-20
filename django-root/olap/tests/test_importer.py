import datetime

from django.test.testcases import TestCase
from django.utils.timezone import get_current_timezone

from dashboard.tests.factories import CourseFactory
from olap.lms_import import ImportLmsData
from olap.models import LMSSession
from olap.models import PageVisit
from olap.tests.factories import LMSUserFactory
from olap.tests.factories import PageFactory
from olap.tests.factories import PageVisitFactory


class ImporterSessionCalcTests(TestCase):
    """
       Test that session calculation is done correctly, for a number of cases.

       For each case, construct some PageVisits with predetermined times between the visits.
       Then hand those visits to the session calculator, and check the sessions it creates.
    """
    def setUp(self):
        self.offering = CourseFactory()
        self.lms_user = LMSUserFactory(course_offering=self.offering)
        self.page = PageFactory()

    def test_session_calculation(self):

        mins_in_24h10m = 24*60+10

        cases = (
            # PageVisit t= Inputs # Expected session starts, durations and pageviews
            ((),                  []), # No visits => no sessions
            ((0, ),               [(0, 0, 1)]), # One visit => one session of 0 mins
            ((0, 20),             [(0, 20, 2)]), # Two visits 20m apart => one session of 20 mins
            ((0, 50),             [(0, 0, 1), (50, 0, 1)]), # Two visits 50m apart => two sessions of 0 mins
            ((0, 20, 30),         [(0, 30, 3)]), # Three visits 20 then 10 mins apart => one session of 30 mins
            ((0, 20, 50),         [(0, 50, 3)]), # Three visits 20 then 30 mins apart => one session of 50 mins
            ((0, 40, 80),         [(0, 80, 3)]), # Three visits 40 then 40 mins apart => one session of 80 mins
            ((0, 40, 90),         [(0, 40, 2), (90, 0, 1)]), # Three visits 40 then 50 mins apart => two sessions
            ((0, mins_in_24h10m), [(0, 0, 1), (mins_in_24h10m, 0, 1)]), # Two visits 1d10m apart => two sessions
        )

        start_datetime = datetime.datetime(2016, 7, 21, 8, 47, 21, tzinfo=get_current_timezone())

        importer = ImportLmsData(self.offering)

        for visit_event_times, expected_outputs in cases:
            # Erase results from last case
            PageVisit.objects.all().delete()
            LMSSession.objects.all().delete()
            # Turn tuple of time-in-minutes between views, into a tuple of visit datetimes
            visit_datetimes = (start_datetime + datetime.timedelta(minutes=int(m)) for m in visit_event_times)

            # Create the series of visits, spaced apart by the event times
            for dt in visit_datetimes:
                visit = PageVisitFactory(lms_user=self.lms_user, page=self.page, visited_at=dt)

            # Run the session calculator
            importer.calculate_session_for_user(self.lms_user)

            # Analyse the sessions created by the calculator, and turn the start time, duration and pageviews into
            # tuples for comparison against the expected result
            actual_outputs = []
            for session in LMSSession.objects.all():
                session_start_timedelta = session.first_visit.visited_at - start_datetime
                session_start_time_in_mins = int(session_start_timedelta.total_seconds() / 60)
                actual_outputs.append((session_start_time_in_mins, session.session_length_in_mins, session.pageviews))

            # Now that we've assembled tuples of session starts, durations and pageviews, do they match what we expect?
            self.assertEqual(expected_outputs, actual_outputs)
