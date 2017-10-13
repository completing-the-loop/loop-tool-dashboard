import csv
from datetime import datetime
import io
import re
import unicodedata
from zipfile import ZipFile

from django.db import connection
from django.utils import dateparse

from dashboard.models import CourseOffering
from olap.models import LMSSession
from olap.models import LMSUser
from olap.models import Page
from olap.models import PageVisit
from olap.models import SubmissionAttempt
from olap.models import SubmissionType
from olap.models import SummaryCourseAssessmentVisitsByDayInWeek
from olap.models import SummaryCourseCommunicationVisitsByDayInWeek
from olap.models import SummaryCourseVisitsByDayInWeek
from olap.models import SummaryDiscussion
from olap.models import SummaryForum
from olap.models import SummaryParticipatingUsersByDayInWeek
from olap.models import SummaryPost
from olap.models import SummarySessionAverageLengthByDayInWeek
from olap.models import SummarySessionAveragePagesPerSessionByDayInWeek
from olap.models import SummarySessionsByDayInWeek
from olap.models import SummaryUniquePageViewsByDayInWeek


class LMSImportError(Exception):
    pass


class LMSImportFileError(LMSImportError):
    def __init__(self, import_file, msg=None):
        if msg is None:
            msg = "Error in import file {}".format(import_file)
        super().__init__(msg)
        self.import_file = import_file


class LMSImportDataError(LMSImportError):
    def __init__(self, errors, msg=None):
        if msg is None:
            msg = "One or more errors in import data"
        super().__init__(msg, errors)
        self.errors = errors


class ImportLmsData(object):
    SESSION_LENGTH_MINS = 40

    staff_list = []
    sitetree = {}

    def __init__(self, course_offering, file_path, just_clear=False):
        self.just_clear = just_clear
        self.course_import_path = file_path
        self.course_offering = course_offering

    def set_latest_activity(self):
        latest_activity = []

        try:
            latest_activity.append(PageVisit.objects.filter(page__course_offering=self.course_offering).latest('visited_at').visited_at)
        except PageVisit.DoesNotExist:
            pass

        try:
            latest_activity.append(SubmissionAttempt.objects.filter(page__course_offering=self.course_offering).latest('attempted_at').attempted_at)
        except SubmissionAttempt.DoesNotExist:
            pass

        try:
            latest_activity.append(SummaryPost.objects.filter(page__course_offering=self.course_offering).latest('posted_at').posted_at)
        except SummaryPost.DoesNotExist:
            pass

        if len(latest_activity):
            self.course_offering.last_activity_at = max(latest_activity)
        else:
            self.course_offering.last_activity_at = None
        self.course_offering.save()

    def process(self):
        errors = []
        offering = self.course_offering
        if self.just_clear:
            print("Removing old data for", offering)
            self.remove_olap_data()
            self.set_latest_activity()
            return

        if offering.lms_type == CourseOffering.LMS_TYPE_BLACKBOARD:
            print("Importing course offering data for", offering)
            lms_import = BlackboardImport(self.course_import_path, offering)
            errors = lms_import.process_import_data()

            print("Processing user sessions for", offering)
            self._calculate_sessions()

            # print("Populating summary data for {}".format(course_offering))
            # self._populate_summary_tables(course_offering, lms_import.get_assessment_types(), lms_import.get_communication_types())
            print("Skipping populating summary data for", offering)

        if len(errors):
            # TODO: Email the admins with the list of errors
            raise LMSImportDataError(errors)

        self.set_latest_activity()

    def remove_olap_data(self):
        offering = self.course_offering
        # First the OLAP Tables
        LMSUser.objects.filter(course_offering=offering).delete()
        Page.objects.filter(course_offering=offering).delete()
        PageVisit.objects.filter(page__course_offering=offering).delete()
        LMSSession.objects.filter(course_offering=offering).delete()
        SubmissionAttempt.objects.filter(page__course_offering=offering).delete()
        SubmissionType.objects.filter(course_offering=offering).delete()
        SummaryPost.objects.filter(page__course_offering=offering).delete()

        # # Next cleanup the Summary Tables
        # connection.execute("DELETE FROM Summary_Courses");
        SummaryForum.objects.filter(course_offering=offering).delete()
        SummaryDiscussion.objects.filter(course_offering=offering).delete()
        SummaryPost.objects.filter(page__course_offering=offering).delete()
        SummaryCourseVisitsByDayInWeek.objects.filter(course_offering=offering).delete()
        SummaryCourseCommunicationVisitsByDayInWeek.objects.filter(course_offering=offering).delete()
        SummaryCourseAssessmentVisitsByDayInWeek.objects.filter(course_offering=offering).delete()
        SummarySessionsByDayInWeek.objects.filter(course_offering=offering).delete()
        SummarySessionAverageLengthByDayInWeek.objects.filter(course_offering=offering).delete()
        SummarySessionAveragePagesPerSessionByDayInWeek.objects.filter(course_offering=offering).delete()
        SummaryParticipatingUsersByDayInWeek.objects.filter(course_offering=offering).delete()
        SummaryUniquePageViewsByDayInWeek.objects.filter(course_offering=offering).delete()

    def _store_session(self, session_visits_list):
        first_visit = session_visits_list[0]
        session_start = first_visit.visited_at
        session_end = session_visits_list[-1].visited_at
        session_duration = int((session_end - session_start).total_seconds() / 60)
        pageviews = len(session_visits_list)
        session = LMSSession(course_offering=self.course_offering, first_visit=first_visit, pageviews=pageviews, session_length_in_mins=session_duration)
        session.save()
        session_visits_list_ids = (v.id for v in session_visits_list)
        PageVisit.objects.filter(id__in=session_visits_list_ids).update(session=session)

    def calculate_session_for_user(self, lms_user):

        """
            For a given LMS user, aggregate page views into sessions.
            A session includes all visits by a user, where the time difference between subsequent views
            does not exceed SESSION_LENGTH_MINS.  Sessions don't care about which page got visited, only that there
            were visits.

            Algorithm to Determine Sessions:
             - iterate over visits looking for a gap between visits greater than SESSION_LENGTH_MINS
             - take the views with gaps shorter than SESSION_LENGTH_MINS and create a session to span them
             - update the session FK in each visit spanned by the session, to the session
        """
        visits = PageVisit.objects.filter(lms_user=lms_user).order_by('visited_at')

        if len(visits) == 0:
            # No visits => no sessions.
            return

        prev_visit_time = None
        visits_list_for_this_session = []
        for visit in visits:
            if prev_visit_time is None:
                prev_visit_time = visit.visited_at
                visits_list_for_this_session = [visit]
                continue

            this_visit_time = visit.visited_at
            td = this_visit_time - prev_visit_time
            total_seconds = td.total_seconds()
            session_duration = int(total_seconds / 60)
            if session_duration > self.SESSION_LENGTH_MINS:
                # Time since previous visit is greater than max session length, so we should start a new session.
                # Save the visits we found so far.
                self._store_session(visits_list_for_this_session)
                visits_list_for_this_session = [visit]
            else:
                visits_list_for_this_session.append(visit)
            prev_visit_time = this_visit_time

        # If that was the final visit, store it as a session.
        self._store_session(visits_list_for_this_session)

    def _calculate_sessions(self):
        # For each user (i.e., student), calculate visit sessions.
        lms_users = LMSUser.objects.filter(course_offering=self.course_offering)
        for lms_user in lms_users:
            self.calculate_session_for_user(lms_user)

    def _populate_summary_tables(self, course_offering, assessment_types, communication_types):
        """
            Produces summary tables Summary_CourseVisitsByDayInWeek, Summary_CourseCommunicationVisitsByDayInWeek
            Summary_CourseAssessmentVisitsByDayInWeek, Summary_SessionAverageLengthByDayInWeek, Summary_SessionAveragePagesPerSessionByDayInWeek
            Summary_ParticipatingUsersByDayInWeek, Summary_UniquePageViewsByDayInWeek
        """

        excluded_content_types = communication_types + assessment_types
        course_weeks = course_offering.get_weeks()
        excluded_types_placeholders = ",".join(['%s' for s in excluded_content_types])
        communication_types_placeholders = ','.join("%s" for s in communication_types)
        assessment_types_placeholders = ','.join("%s" for s in assessment_types)

        # Populate Summary_CourseVisitsByDayInWeek - only contains content items
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, SUM(F.pageview) AS pageviews, F.course_id FROM olap_dimdate D LEFT JOIN olap_pagevisit F ON D.id = F.date_id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s AND F.module NOT IN ({}) GROUP BY D.date_week, D.date_dayinweek".format(excluded_types_placeholders)
            cursor.execute(sql, [course_weeks, course_offering.id] + excluded_content_types)
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryCourseVisitsByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course_offering=course_offering)
                summary.save()

        # Populate Summary_CourseCommunicationVisitsByDayInWeek - only contains forums
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, SUM(F.pageview) AS pageviews, F.course_id FROM olap_dimdate D LEFT JOIN olap_pagevisit F ON D.id = F.date_id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s AND F.module IN ({}) GROUP BY D.date_week, D.date_dayinweek".format(communication_types_placeholders)
            cursor.execute(sql, [course_weeks, course_offering.id] + communication_types)
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryCourseCommunicationVisitsByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course_offering=course_offering)
                summary.save()

        # Populate Summary_CourseAssessmentVisitsByDayInWeek - only contains quiz and assign
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, SUM(F.pageview) AS pageviews, F.course_id FROM olap_dimdate D LEFT JOIN olap_pagevisit F ON D.id = F.date_id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s AND F.module IN ({}) GROUP BY D.date_week, D.date_dayinweek".format(assessment_types_placeholders)
            cursor.execute(sql, [course_weeks, course_offering.id] + assessment_types)
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryCourseAssessmentVisitsByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course_offering=course_offering)
                summary.save()

        # Populate Summary_SessionAverageLengthByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT S.date_year, S.date_week, S.date_dayinweek, AVG(S.session_length_in_mins), S.course_id FROM olap_dimsession S WHERE S.date_dayinweek IN (0,1,2,3,4,5,6) AND S.date_week IN %s AND S.course_id=%s GROUP BY S.date_week, S.date_dayinweek"
            cursor.execute(sql, [course_weeks, course_offering.id])
            results = cursor.fetchall()
            for row in results:
                session_average_in_minutes = row[3] if row[3] is not None else 0
                summary = SummarySessionAverageLengthByDayInWeek(date_year=row[0], date_week=row[1], date_dayinweek=row[2], session_average_in_minutes=session_average_in_minutes, course_offering=course_offering)
                summary.save()

        # Populate Summary_SessionAveragePagesPerSessionByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT S.date_year, S.date_week, S.date_dayinweek, AVG(S.pageviews), S.course_id FROM olap_dimsession S WHERE S.date_dayinweek IN (0,1,2,3,4,5,6) AND S.date_week IN %s AND S.course_id=%s GROUP BY S.date_week, S.date_dayinweek"
            cursor.execute(sql, [course_weeks, course_offering.id])
            results = cursor.fetchall()
            for row in results:
                pages_per_session = row[3] if row[3] is not None else 0
                summary = SummarySessionAveragePagesPerSessionByDayInWeek(date_year=row[0], date_week=row[1], date_dayinweek=row[2], pages_per_session=pages_per_session, course_offering=course_offering)
                summary.save()

        # Populate Summary_SessionsByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT S.date_year, S.date_week, S.date_dayinweek, COUNT(DISTINCT S.session_id), S.course_id FROM olap_dimsession S WHERE S.date_dayinweek IN (0,1,2,3,4,5,6) AND S.date_week IN %s AND S.course_id=%s GROUP BY S.date_week, S.date_dayinweek"
            cursor.execute(sql, [course_weeks, course_offering.id])
            results = cursor.fetchall()
            for row in results:
                sessions = row[3] if row[3] is not None else 0
                summary = SummarySessionsByDayInWeek(date_year=row[0], date_week=row[1], date_dayinweek=row[2], sessions=sessions, course_offering=course_offering)
                summary.save()

        # Populate Summary_ParticipatingUsersByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, SUM(F.pageview), F.course_id FROM olap_dimdate D LEFT JOIN olap_pagevisit F ON D.id = F.date_id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s GROUP BY D.date_week, D.date_dayinweek;"
            cursor.execute(sql, [course_weeks, course_offering.id])
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryParticipatingUsersByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course_offering=course_offering)
                summary.save()

        # Populate Summary_UniquePageViewsByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, COUNT(DISTINCT F.page_id), F.course_id FROM olap_pagevisit F INNER JOIN olap_dimdate D ON F.date_id = D.id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s GROUP BY D.date_week, D.date_dayinweek"
            cursor.execute(sql, [course_weeks, course_offering.id])
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryUniquePageViewsByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course_offering=course_offering)
                summary.save()

    """
    # This is what's left of the DimDates creation stuff, so we can see
    # How they generated certain date related stuff.
                id=datetime.datetime.strftime(date_val, "%d-%b-%y"),
                date_year=date_val.year,
                date_month=date_val.month,
                date_day=date_val.day,
                date_dayinweek=date_val.weekday(),
                date_week=date_val.isocalendar()[1],
                unixtimestamp=date_val.timestamp(),
            )

    # Would be good to have unit tests that catch these situations (so we know why this code exists)
            if date_obj.date_month == 12 and date_obj.date_week <= 1:
                date_obj.date_week = 52
            if date_obj.date_month == 1 and date_obj.date_week >= 52:
                date_obj.date_week = 1
    """

class BaseLmsImport(object):

    def __init__(self, course_import_path, course_offering):
        self.course_offering = course_offering
        self.course_import_path = course_import_path
        self.error_list = []

    def process_import_data(self):
        raise NotImplementedError("'process_import_data' must be implemented")

    def get_assessment_types(self):
        raise NotImplementedError("'get_assessment_types' must be implemented")

    def get_communication_types(self):
        raise NotImplementedError("'get_communication_types' must be implemented")

    def _add_error(self, error_msg):
        self.error_list.append(error_msg)


class BlackboardImport(BaseLmsImport):
    USERS_FILE = 'user.txt'
    RESOURCES_FILE = 'resources.txt'
    POSTS_FILE = 'forums.txt'
    SUBMISSIONS_FILE = 'assessments.txt'
    ACTIVITY_FILE = 'activity.txt'

    USERS_FIELDNAMES = ['user_key', 'firstname', 'lastname', 'username', 'email']
    RESOURCES_FIELDNAMES = ['content_key', 'parent_content_key', 'title', 'resource_type']
    POSTS_FIELDNAMES = ['forum_key', 'user_key', 'thread', 'post', 'timestamp']
    SUBMISSIONS_FIELDNAMES = ['user_key', 'content_key', 'user_grade', 'timestamp']
    ACTIVITY_FIELDNAMES = ['user_key', 'content_key', 'forum_key', 'timestamp']

    def get_assessment_types(self):
        return ['assessment/x-bb-qti-test', 'course/x-bb-courseassessment', 'resource/x-turnitin-assignment']

    def get_communication_types(self):
        return ['resource/x-bb-discussionboard', 'course/x-bb-collabsession', 'resource/x-bb-discussionfolder']

    def process_import_data(self):
        self._process_csv(self.USERS_FILE, self._process_users)
        self._process_csv(self.RESOURCES_FILE, self._process_resources)
        self._process_csv(self.RESOURCES_FILE, self._process_resource_parents)
        # self._process_csv(self.POSTS_FILE, self._process_posts)
        self._process_csv(self.SUBMISSIONS_FILE, self._process_submission_attempts)
        self._process_csv(self.ACTIVITY_FILE, self._process_access_log)

        return self.error_list

    def _process_csv(self, file_name, process_callable):
        with ZipFile(self.course_import_path) as import_zip:
            with import_zip.open(file_name) as csv_file:
                csv_file = io.TextIOWrapper(csv_file, encoding='UTF-8', newline='')
                csv_data = csv.DictReader(csv_file, delimiter='|')
                process_callable(csv_data)

    def _process_users(self, users_data):
        """
        Extracts users from the course import files and updates/inserts into the LMSUser table
        """
        if set(users_data.fieldnames) != set(self.USERS_FIELDNAMES):
            raise LMSImportFileError(self.USERS_FILE, 'User data columns do not match {}'.format(self.USERS_FIELDNAMES))

        for row in users_data:
            values = {
                'firstname': row['firstname'],
                'lastname': row['lastname'],
                'username': row['username'],
                'email': row['email'],
            }
            user, created = LMSUser.objects.update_or_create(course_offering=self.course_offering, lms_user_id=row['user_key'], defaults=values)

    def _process_resources(self, resources_data):
        """
        Extracts pages/resources from the course import files and updates/inserts into the Page table
        """
        if set(resources_data.fieldnames) != set(self.RESOURCES_FIELDNAMES):
            raise LMSImportFileError(self.RESOURCES_FILE, 'Resource data columns do not match {}'.format(self.RESOURCES_FIELDNAMES))

        # Set the parent to None until all resources are inserted
        for row in resources_data:
            values = {
                'title': row['title'],
                'content_type': row['resource_type'],
                'parent_id': None,
            }
            resource, created = Page.objects.update_or_create(course_offering=self.course_offering, content_id=row['content_key'], defaults=values)

    def _process_resource_parents(self, resources_data):
        """
        Go through the pages/resources from the course import files again and find the parents, deleting any pages whose parent is missing
        """
        for row in resources_data:
            if row['parent_content_key']:
                content_page = Page.objects.get(content_id=row['content_key'])
                try:
                    parent_page = Page.objects.get(content_id=row['parent_content_key'])
                    content_page.parent = parent_page
                    content_page.save()
                except Page.DoesNotExist:
                    self._add_error('Unable to find parent resource {}'.format(row['parent_content_key']))

    def _process_submission_attempts(self, submissions_data):
        """
        Extracts submission attempts from the course import files and updates/inserts into the submission attempts table
        """
        if set(submissions_data.fieldnames) != set(self.SUBMISSIONS_FIELDNAMES):
            raise LMSImportFileError(self.SUBMISSIONS_FILE, 'Submissions data columns do not match {}'.format(self.SUBMISSIONS_FIELDNAMES))

        for row in submissions_data:
            try:
                user = LMSUser.objects.get(lms_user_id=row['user_key'])
            except LMSUser.DoesNotExist:
                self._add_error('Unable to find user {} for submission attempt'.format(row['user_key']))
                continue

            try:
                page = Page.objects.get(content_id=row['content_key'])
            except Page.DoesNotExist:
                self._add_error('Unable to find page {} for submission attempt'.format(row['content_key']))
                continue

            try:
                attempted_at = dateparse.parse_datetime(row['timestamp'])
                if attempted_at is None:
                    self._add_error('Timestamp {} for submission attempt is not a valid format'.format(row['timestamp']))
                    continue
            except ValueError:
                self._add_error('Timestamp {} for submission attempt is not a valid datetime'.format(row['timestamp']))
                continue

            if attempted_at < self.course_offering.start_datetime or attempted_at > self.course_offering.end_datetime:
                self._add_error('Timestamp {} for submission attempt is outside course offering start/end'.format(row['timestamp']))
                continue

            values = {
                'grade': row['user_grade'],
                'attempted_at': attempted_at,
            }
            submission, created = SubmissionAttempt.objects.update_or_create(lms_user=user, page=page, defaults=values)

    def _process_access_log(self, activity_data):
        """
        Extracts user activity from the course import files and updates/inserts into the page visits table
        """
        if set(activity_data.fieldnames) != set(self.ACTIVITY_FIELDNAMES):
            raise LMSImportFileError(self.ACTIVITY_FILE, 'Activity data columns do not match {}'.format(self.ACTIVITY_FIELDNAMES))

        for row in activity_data:
            try:
                user = LMSUser.objects.get(lms_user_id=row['user_key'])
            except LMSUser.DoesNotExist:
                self._add_error('Unable to find user {} for activity'.format(row['user_key']))
                continue

            try:
                page = Page.objects.get(content_id=row['content_key'])
            except Page.DoesNotExist:
                self._add_error('Unable to find resource {} for activity'.format(row['content_key']))
                continue

            try:
                visited_at = dateparse.parse_datetime(row['timestamp'])
                if visited_at is None:
                    self._add_error('Timestamp {} for access activity is not a valid format'.format(row['timestamp']))
                    continue
            except ValueError:
                self._add_error('Timestamp {} for access activity is not a valid datetime'.format(row['timestamp']))
                continue

            if visited_at < self.course_offering.start_datetime or visited_at > self.course_offering.end_datetime:
                self._add_error('Timestamp {} for access activity is outside course offering start/end'.format(row['timestamp']))
                continue

            values = {
                'visited_at': visited_at,
            }
            page_visit, created = PageVisit.objects.update_or_create(lms_user=user, page=page, defaults=values)
