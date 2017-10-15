import csv
import datetime
import io
from textwrap import dedent

from django.test.testcases import TestCase
from django.utils.timezone import get_current_timezone

from dashboard.tests.factories import CourseOfferingFactory
from olap.lms_import import BlackboardImport
from olap.lms_import import ImportLmsData
from olap.lms_import import LMSImportFileError
from olap.models import LMSSession, SummaryPost
from olap.models import LMSUser
from olap.models import Page
from olap.models import PageVisit
from olap.models import SubmissionAttempt
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
        self.offering = CourseOfferingFactory()
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

        importer = ImportLmsData(self.offering, 'ignore.txt')

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

        importer = ImportLmsData(self.offering, 'ignore.txt')
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

        importer = ImportLmsData(self.offering, 'ignore.txt')
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


class ImportUsersTestCase(TestCase):
    """
    Tests to ensure that user imports are handled correctly
    """

    def setUp(self):
        self.offering = CourseOfferingFactory()

    def test_invalid_column_names(self):
        test_users = """\
            user_key|username|invalid_col
            1|fred|value
        """

        csv_data = io.StringIO(dedent(test_users))
        user_data = csv.DictReader(csv_data, delimiter='|')

        importer = BlackboardImport('ignore.zip', self.offering)

        with self.assertRaises(LMSImportFileError):
            importer._process_users(user_data)

    def test_valid_data(self):
        test_users = """\
            user_key|username|firstname|lastname|email
            1|fred|Fred|Jones|fred@email.com
        """

        csv_data = io.StringIO(dedent(test_users))
        user_data = csv.DictReader(csv_data, delimiter='|')

        importer = BlackboardImport('ignore.zip', self.offering)
        importer._process_users(user_data)

        self.assertTrue(LMSUser.objects.filter(lms_user_id=1, username='fred', firstname='Fred', lastname='Jones', email='fred@email.com', course_offering=self.offering).exists())


class ImportResourcesTestCase(TestCase):
    """
    Tests to ensure that resource imports are handled correctly
    """

    def setUp(self):
        self.offering = CourseOfferingFactory()

    def test_invalid_column_names(self):
        test_resources = """\
            content_key|parent_content_key|invalid_col
            1|2|value
        """

        csv_data = io.StringIO(dedent(test_resources))
        resources_data = csv.DictReader(csv_data, delimiter='|')

        importer = BlackboardImport('ignore.zip', self.offering)

        with self.assertRaises(LMSImportFileError):
            importer._process_resources(resources_data)

    def test_valid_data(self):
        test_resources = """\
            content_key|parent_content_key|title|resource_type
            1||Parent page|resource/x-bb-document
            2|1|Child page|resource/x-bb-document
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        csv_data = io.StringIO(dedent(test_resources))
        resources_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_resources(resources_data)

        self.assertTrue(Page.objects.filter(content_id=1, parent__isnull=True, title='Parent page', content_type='resource/x-bb-document', is_forum=False, course_offering=self.offering).exists())
        self.assertTrue(Page.objects.filter(content_id=2, parent__isnull=True, title='Child page', content_type='resource/x-bb-document', is_forum=False, course_offering=self.offering).exists())

    def test_valid_parents_data(self):
        test_resources = """\
            content_key|parent_content_key|title|resource_type
            1||Parent page|resource/x-bb-document
            2|1|Child page|resource/x-bb-document
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        parent_page = PageFactory(content_id=1, course_offering=self.offering)
        PageFactory(content_id=2, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_resources))
        resources_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_resource_parents(resources_data)
        self.assertTrue(Page.objects.filter(content_id=1, parent__isnull=True, course_offering=self.offering).exists())
        self.assertTrue(Page.objects.filter(content_id=2, parent=parent_page, course_offering=self.offering).exists())

    def test_missing_parents_data(self):
        test_resources = """\
            content_key|parent_content_key|title|resource_type
            1||Parent page|resource/x-bb-document
            2|500|Child page|resource/x-bb-document
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        PageFactory(content_id=1, course_offering=self.offering)
        PageFactory(content_id=2, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_resources))
        resources_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_resource_parents(resources_data)
        self.assertEqual(len(importer.error_list), 1)


class ImportSubmissionAttemptsTestCase(TestCase):
    """
    Tests to ensure that submission attempts imports are handled correctly
    """

    def setUp(self):
        self.offering = CourseOfferingFactory(start_date=datetime.date(2017, 7, 3), no_weeks=14)

    def test_invalid_column_names(self):
        test_submissions = """\
            user_key|content_key|invalid_col
            1|2|value
        """

        csv_data = io.StringIO(dedent(test_submissions))
        submissions_data = csv.DictReader(csv_data, delimiter='|')

        importer = BlackboardImport('ignore.zip', self.offering)

        with self.assertRaises(LMSImportFileError):
            importer._process_submission_attempts(submissions_data)

    def test_valid_data(self):
        test_submissions = """\
            user_key|content_key|user_grade|timestamp
            1|1|0|2017-10-05 13:30:00+00:00
            2|1|10.5|2017-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        attempt_dt = datetime.datetime(2017, 10, 5, 13, 30, 0, tzinfo=datetime.timezone.utc)
        page = PageFactory(content_id=1, course_offering=self.offering)
        user1 = LMSUserFactory(lms_user_id=1, course_offering=self.offering)
        user2 = LMSUserFactory(lms_user_id=2, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_submissions))
        submissions_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_submission_attempts(submissions_data)

        self.assertTrue(SubmissionAttempt.objects.filter(page=page, lms_user=user1, grade='0', attempted_at=attempt_dt).exists())
        self.assertTrue(SubmissionAttempt.objects.filter(page=page, lms_user=user2, grade='10.5', attempted_at=attempt_dt).exists())


    def test_missing_related_objects(self):
        test_submissions = """\
            user_key|content_key|user_grade|timestamp
            1|500|0|2017-10-05 13:30:00+00:00
            500|1|10.5|2017-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        PageFactory(content_id=1, course_offering=self.offering)
        LMSUserFactory(lms_user_id=1, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_submissions))
        submissions_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_submission_attempts(submissions_data)

        self.assertEqual(len(importer.error_list), 2)


    def test_invalid_attempt_datetimes(self):
        test_submissions = """\
            user_key|content_key|user_grade|timestamp
            1|1|0|2018-10-05 13:30:00+00:00
            2|1|10.5|2016-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        PageFactory(content_id=1, course_offering=self.offering)
        LMSUserFactory(lms_user_id=1, course_offering=self.offering)
        LMSUserFactory(lms_user_id=2, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_submissions))
        submissions_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_submission_attempts(submissions_data)

        self.assertEqual(len(importer.error_list), 2)


class ImportPostsTestCase(TestCase):
    """
    Tests to ensure that the posts imports are handled correctly
    """

    def setUp(self):
        self.offering = CourseOfferingFactory(start_date=datetime.date(2017, 7, 3), no_weeks=14)

    def test_invalid_column_names(self):
        test_posts = """\
            forum_key|user_key|invalid_col
            1|2|value
        """

        csv_data = io.StringIO(dedent(test_posts))
        posts_data = csv.DictReader(csv_data, delimiter='|')

        importer = BlackboardImport('ignore.zip', self.offering)

        with self.assertRaises(LMSImportFileError):
            importer._process_posts(posts_data)

    def test_valid_data(self):
        test_posts = """\
            forum_key|user_key|thread|post|timestamp
            1|1|Name of thread|User 1 post|2017-10-05 13:30:00+00:00
            1|2|Name of thread|User 2 post|2017-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        posted_dt = datetime.datetime(2017, 10, 5, 13, 30, 0, tzinfo=datetime.timezone.utc)
        page = PageFactory(content_id=1, is_forum=True, course_offering=self.offering)
        user1 = LMSUserFactory(lms_user_id=1, course_offering=self.offering)
        user2 = LMSUserFactory(lms_user_id=2, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_posts))
        posts_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_posts(posts_data)

        self.assertTrue(SummaryPost.objects.filter(page=page, lms_user=user1, posted_at=posted_dt).exists())
        self.assertTrue(SummaryPost.objects.filter(page=page, lms_user=user2, posted_at=posted_dt).exists())


    def test_missing_related_objects(self):
        test_posts = """\
            forum_key|user_key|thread|post|timestamp
            1|500|Name of thread|User 1 post|2017-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        PageFactory(content_id=1, is_forum=True, course_offering=self.offering)
        LMSUserFactory(lms_user_id=1, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_posts))
        posts_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_posts(posts_data)

        self.assertEqual(len(importer.error_list), 1)


    def test_invalid_access_datetimes(self):
        test_posts = """\
            forum_key|user_key|thread|post|timestamp
            1|1|Name of thread|User 1 post|2016-10-05 13:30:00+00:00
            1|2|Name of thread|User 2 post|2018-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        PageFactory(content_id=1, is_forum=True, course_offering=self.offering)
        LMSUserFactory(lms_user_id=1, course_offering=self.offering)
        LMSUserFactory(lms_user_id=2, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_posts))
        posts_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_posts(posts_data)

        self.assertEqual(len(importer.error_list), 2)


class ImportActivityTestCase(TestCase):
    """
    Tests to ensure that access activity log imports are handled correctly
    """

    def setUp(self):
        self.offering = CourseOfferingFactory(start_date=datetime.date(2017, 7, 3), no_weeks=14)

    def test_invalid_column_names(self):
        test_activity = """\
            user_key|content_key|invalid_col
            1|2|value
        """

        csv_data = io.StringIO(dedent(test_activity))
        activity_data = csv.DictReader(csv_data, delimiter='|')

        importer = BlackboardImport('ignore.zip', self.offering)

        with self.assertRaises(LMSImportFileError):
            importer._process_access_log(activity_data)

    def test_valid_data(self):
        test_activity = """\
            user_key|content_key|forum_key|timestamp
            1|1||2017-10-05 13:30:00+00:00
            2|1||2017-10-05 13:30:00+00:00
            2||2|2017-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        visit_dt = datetime.datetime(2017, 10, 5, 13, 30, 0, tzinfo=datetime.timezone.utc)
        resource_page = PageFactory(content_id=1, is_forum=False, course_offering=self.offering)
        post_page = PageFactory(content_id=2, is_forum=True, course_offering=self.offering)
        user1 = LMSUserFactory(lms_user_id=1, course_offering=self.offering)
        user2 = LMSUserFactory(lms_user_id=2, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_activity))
        activity_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_access_log(activity_data)

        self.assertTrue(PageVisit.objects.filter(page=resource_page, lms_user=user1, visited_at=visit_dt).exists())
        self.assertTrue(PageVisit.objects.filter(page=resource_page, lms_user=user2, visited_at=visit_dt).exists())
        self.assertTrue(PageVisit.objects.filter(page=post_page, lms_user=user2, visited_at=visit_dt).exists())


    def test_missing_related_objects(self):
        test_activity = """\
            user_key|content_key|forum_key|timestamp
            1|500||2017-10-05 13:30:00+00:00
            1||500|2017-10-05 13:30:00+00:00
            500|1||2017-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        PageFactory(content_id=1, is_forum=False, course_offering=self.offering)
        LMSUserFactory(lms_user_id=1, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_activity))
        activity_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_access_log(activity_data)

        self.assertEqual(len(importer.error_list), 3)


    def test_invalid_access_datetimes(self):
        test_activity = """\
            user_key|content_key|forum_key|timestamp
            1|1||2018-10-05 13:30:00+00:00
            2|1||2016-10-05 13:30:00+00:00
        """

        importer = BlackboardImport('ignore.zip', self.offering)

        PageFactory(content_id=1, course_offering=self.offering)
        LMSUserFactory(lms_user_id=1, course_offering=self.offering)
        LMSUserFactory(lms_user_id=2, course_offering=self.offering)

        csv_data = io.StringIO(dedent(test_activity))
        activity_data = csv.DictReader(csv_data, delimiter='|')
        importer._process_access_log(activity_data)

        self.assertEqual(len(importer.error_list), 2)
