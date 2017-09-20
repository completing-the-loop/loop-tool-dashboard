import datetime

from django.test.testcases import TestCase
from django.utils.timezone import get_current_timezone

from dashboard.tests.factories import CourseFactory
from olap.lms_import import ImportLmsData
from olap.models import LMSSession
from olap.models import LMSUser
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
        self.test_start_datetime = datetime.datetime(2016, 7, 21, 8, 47, 21, tzinfo=get_current_timezone())


    def test_session_calculation(self):
        mins_in_24h10m = 24 * 60 + 10

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

        lms_user = LMSUserFactory(course_offering=self.offering)
        page = PageFactory()

        importer = ImportLmsData(self.offering)

        for visit_event_times, expected_outputs in cases:
            # Erase results from last case
            PageVisit.objects.all().delete()
            LMSSession.objects.all().delete()
            # Turn tuple of time-in-minutes between views, into a tuple of visit datetimes
            visit_datetimes = (self.test_start_datetime + datetime.timedelta(minutes=int(m)) for m in visit_event_times)

            # Create the series of visits, spaced apart by the event times
            for dt in visit_datetimes:
                visit = PageVisitFactory(lms_user=lms_user, page=page, visited_at=dt)

            # Run the session calculator
            importer.calculate_session_for_user(lms_user)

            # Analyse the sessions created by the calculator, and turn the start time, duration and pageviews into
            # tuples for comparison against the expected result
            actual_outputs = []
            for session in LMSSession.objects.all():
                session_start_timedelta = session.first_visit.visited_at - self.test_start_datetime
                session_start_time_in_mins = int(session_start_timedelta.total_seconds() / 60)
                actual_outputs.append((session_start_time_in_mins, session.session_length_in_mins, session.pageviews))

            # Now that we've assembled tuples of session starts, durations and pageviews, do they match what we expect?
            self.assertEqual(expected_outputs, actual_outputs)

    def test_only_include_pages_for_a_given_user(self):
        # Have four pages split across two users.  Make sure the calculated sessions for both users are correct,
        # especially the aspect that visits due to one user are ignored when calculating the session for another user.

        u1 = LMSUserFactory(course_offering=self.offering)
        u1_p1 = PageFactory()
        u1_p2 = PageFactory()

        u2 = LMSUserFactory(course_offering=self.offering)
        u2_p1 = PageFactory()
        u2_p2 = PageFactory()

        orphan = PageFactory()

        # Visits for u1 which should result in a session starting at test_start_dt, lasting 25 mins
        u1_expected_session_start_dt = self.test_start_datetime
        v_u1_p1 = PageVisitFactory(lms_user=u1, page=u1_p1, visited_at=u1_expected_session_start_dt)
        v_u1_p2 = PageVisitFactory(lms_user=u1, page=u1_p2, visited_at=u1_expected_session_start_dt + datetime.timedelta(minutes=25))
        # Visits for u2 which should result in a session starting at test_start_dt+10mins, and lasting 21 mins
        u2_expected_session_start_dt = self.test_start_datetime + datetime.timedelta(minutes=10)
        v_u2_p1 = PageVisitFactory(lms_user=u2, page=u2_p1, visited_at=u2_expected_session_start_dt)
        v_u2_p2 = PageVisitFactory(lms_user=u2, page=u2_p2, visited_at=u2_expected_session_start_dt + datetime.timedelta(minutes=21))

        importer = ImportLmsData(self.offering)
        importer._calculate_sessions()

        sessions = LMSSession.objects.all()
        session_info_extractor = lambda s: (s.first_visit.lms_user, s.first_visit.visited_at, s.session_length_in_mins, s.pageviews)
        extracted_session_info = tuple(session_info_extractor(session) for session in sessions)

        expected_session_info = (
            (u1, u1_expected_session_start_dt, 25, 2),
            (u2, u2_expected_session_start_dt, 21, 2),
        )

        self.assertEqual(expected_session_info, extracted_session_info)

    def test_multiusers_same_pages(self):
        # Have two users accessing almost the same pages.  Make sure the sessions calculated for both users include
        #  the common pages, and the distinct ones.

        u1 = LMSUserFactory(course_offering=self.offering)
        u2 = LMSUserFactory(course_offering=self.offering)

        pre_page = PageFactory()
        common_visit_pages = PageFactory.create_batch(3)
        post_page = PageFactory()

        user_visit_info = {
            u1.pk: (
                (-2, pre_page),
                (0, common_visit_pages[0]),
                (15, common_visit_pages[1]),
                (30, common_visit_pages[2]),
                (39, post_page)
            ),
            u2.pk: (
                (-1, pre_page),
                (5, common_visit_pages[0]),
                (25, common_visit_pages[1]),
                (45, common_visit_pages[2]),
                (89, post_page),
            )
        }

        for user_pk, visit_list in user_visit_info.items():
            user = LMSUser.objects.get(pk=user_pk)
            for visit_offset_mins, page in visit_list:
                visit_obj = PageVisitFactory(lms_user=user, page=page, visited_at=self.test_start_datetime + datetime.timedelta(minutes=visit_offset_mins))

        importer = ImportLmsData(self.offering)
        importer._calculate_sessions()

        sessions = LMSSession.objects.all()
        session_info_extractor = lambda s: (s.first_visit.lms_user, s.first_visit.visited_at, s.session_length_in_mins, s.pageviews)
        extracted_session_info = tuple(session_info_extractor(session) for session in sessions)

        expected_session_info = (
            (u1, self.test_start_datetime + datetime.timedelta(minutes=-2), 41, 5),
            (u2, self.test_start_datetime + datetime.timedelta(minutes=-1), 46, 4),
            (u2, self.test_start_datetime + datetime.timedelta(minutes=89), 0, 1),
        )

        self.assertEqual(expected_session_info, extracted_session_info)
