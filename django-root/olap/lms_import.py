import csv
from datetime import datetime
import io
import itertools
from zipfile import ZipFile

from django.conf import settings
from django.core.mail import send_mail
from django.db.utils import IntegrityError
from django.utils import dateparse
from unipath import Path

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
        super().__init__(msg, import_file)
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

    def write_error_log(self, errors, log_time):
        return self.write_to_error_log('errors_', errors, log_time)

    def write_non_critical_error_log(self, errors, log_time):
        return self.write_to_error_log('non_critical_errors_', errors, log_time)

    def write_to_error_log(self, log_name_prefix, errors, log_time):
        error_log_filename = '{}{}'.format(log_name_prefix, log_time)
        error_log_path = Path(settings.DATA_ERROR_LOGS_DIR, error_log_filename)
        with open(error_log_path, "w") as error_log:
            for error in errors:
                error_log.write("{}\n".format(error))
        return error_log_path

    def process(self):
        errors = set()
        offering = self.course_offering
        if self.just_clear:
            print("Removing old data for", offering)
            self.remove_olap_data()
            self.set_latest_activity()
            return

        if offering.lms_type == CourseOffering.LMS_TYPE_BLACKBOARD:
            print("Importing course offering data for", offering)
            lms_import = BlackboardImport(self.course_import_path, offering)
            all_errors = lms_import.process_import_data()
            # Convert to set to remove duplicates
            errors = set(all_errors['errors'])
            non_critical_errors = set(all_errors['non_critical_errors'])

            print("Processing user sessions for", offering)
            if not len(errors):
                self._calculate_sessions()

        if len(non_critical_errors):
            error_sample = itertools.islice(non_critical_errors, settings.CLOOP_IMPORT_ERRORS_SAMPLE_SIZE)
            log_time = datetime.now()
            error_log_path = self.write_non_critical_error_log(non_critical_errors, log_time)
            msg_text = "There were a total of {} non critical errors during the import of {} at {}.\n\n".format(
                len(non_critical_errors),
                self.course_offering.code,
                log_time,
            )
            msg_text += "A sample of the errors can be found below. The full error log can be found at {}\n\n{}".format(
                error_log_path,
                "\n".join(error_sample),
            )
            send_mail(
                'Non critical errors in import of {}'.format(self.course_offering.code),
                msg_text,
                settings.SERVER_EMAIL,
                settings.CLOOP_IMPORT_ADMINS,
            )

        if len(errors):
            error_sample = itertools.islice(errors, settings.CLOOP_IMPORT_ERRORS_SAMPLE_SIZE)
            log_time = datetime.now()
            error_log_path = self.write_error_log(errors, log_time)
            msg_text = "There were a total of {} errors during the import of {} at {}.\n\n".format(
                len(errors),
                self.course_offering.code,
                log_time,
            )
            msg_text += "A sample of the errors can be found below. The full error log can be found at {}\n\n{}".format(
                error_log_path,
                "\n".join(error_sample),
            )
            send_mail(
                'Errors in import of {}'.format(self.course_offering.code),
                msg_text,
                settings.SERVER_EMAIL,
                settings.CLOOP_IMPORT_ADMINS,
            )
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


class BaseLmsImport(object):

    def __init__(self, course_import_path, course_offering):
        self.course_offering = course_offering
        self.course_import_path = course_import_path
        self.error_list = []
        self.non_critical_error_list = []

    def process_import_data(self):
        raise NotImplementedError("'process_import_data' must be implemented")

    def _add_error(self, error_msg):
        self.error_list.append(error_msg)

    def _add_non_critical_error(self, error_msg):
        self.non_critical_error_list.append(error_msg)


class BlackboardImport(BaseLmsImport):
    USERS_FILE = 'all_user.txt'
    RESOURCES_FILE = 'all_resources.txt'
    POSTS_FILE = 'forums.txt'
    SUBMISSIONS_FILE = 'assessments.txt'
    ACTIVITY_FILE = 'activity.txt'

    USERS_FIELDNAMES = ['user_key', 'firstname', 'lastname', 'username', 'email']
    RESOURCES_FIELDNAMES = ['content_key', 'parent_content_key', 'title', 'resource_type']
    POSTS_FIELDNAMES = ['forum_key', 'user_key', 'thread', 'post', 'timestamp']
    SUBMISSIONS_FIELDNAMES = ['user_key', 'content_key', 'user_grade', 'timestamp']
    ACTIVITY_FIELDNAMES = ['user_key', 'content_key', 'forum_key', 'timestamp']

    FORUM_CONTENT_TYPE = 'resource/x-bb-discussionboard'

    def process_import_data(self):
        print("Processing users")
        self._process_csv(self.USERS_FILE, self._process_users)
        print("Processing resources")
        self._process_csv(self.RESOURCES_FILE, self._process_resources)
        self._process_csv(self.RESOURCES_FILE, self._process_resource_parents)
        print("Processing posts")
        self._process_csv(self.POSTS_FILE, self._process_posts)
        print("Processing submission attempts")
        self._process_csv(self.SUBMISSIONS_FILE, self._process_submission_attempts)
        print("Processing activity")
        self._process_csv(self.ACTIVITY_FILE, self._process_access_log)

        return {
            'errors': self.error_list,
            'non_critical_errors': self.non_critical_error_list
        }

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
            resource, created = Page.objects.update_or_create(course_offering=self.course_offering, content_id=row['content_key'], is_forum=False, defaults=values)

    def _process_resource_parents(self, resources_data):
        """
        Go through the pages/resources from the course import files again and find the parents
        """
        for row in resources_data:
            if row['parent_content_key']:
                content_page = Page.objects.get(content_id=row['content_key'], is_forum=False, course_offering=self.course_offering)
                try:
                    parent_page = Page.objects.get(content_id=row['parent_content_key'], course_offering=self.course_offering)
                    content_page.parent = parent_page
                    content_page.save()
                except Page.DoesNotExist:
                    self._add_non_critical_error('Unable to find parent resource {}'.format(row['parent_content_key']))

    def _process_submission_attempts(self, submissions_data):
        """
        Extracts submission attempts from the course import files and updates/inserts into the submission attempts table
        """
        if set(submissions_data.fieldnames) != set(self.SUBMISSIONS_FIELDNAMES):
            raise LMSImportFileError(self.SUBMISSIONS_FILE, 'Submissions data columns do not match {}'.format(self.SUBMISSIONS_FIELDNAMES))

        for row in submissions_data:
            try:
                user = LMSUser.objects.get(lms_user_id=row['user_key'], course_offering=self.course_offering)
            except LMSUser.DoesNotExist:
                self._add_error('Unable to find user {} for submission attempt'.format(row['user_key']))
                continue

            try:
                page = Page.objects.get(content_id=row['content_key'], is_forum=False, course_offering=self.course_offering)
                if page.content_type not in CourseOffering.assessment_types():
                    self._add_non_critical_error('Resource {} for submission attempt is not an assessment type'.format(page.content_id))
                    continue

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
                self._add_non_critical_error('Timestamp {} for submission attempt is outside course offering start/end'.format(row['timestamp']))
                continue

            try:
                submission = SubmissionAttempt.objects.create(lms_user=user, page=page, attempted_at=attempted_at, grade=row['user_grade'])
            except IntegrityError as e:
                self._add_error('Integrity Error in submission attempt insert: {}'.format(e))

    def _process_access_log(self, activity_data):
        """
        Extracts user activity from the course import files and updates/inserts into the page visits table
        """
        if set(activity_data.fieldnames) != set(self.ACTIVITY_FIELDNAMES):
            raise LMSImportFileError(self.ACTIVITY_FILE, 'Activity data columns do not match {}'.format(self.ACTIVITY_FIELDNAMES))

        batch_size = 10000
        batch = []

        for row in activity_data:
            try:
                user = LMSUser.objects.get(lms_user_id=row['user_key'], course_offering=self.course_offering)
            except LMSUser.DoesNotExist:
                self._add_error('Unable to find user {} for activity'.format(row['user_key']))
                continue

            try:
                # Check if it's a visit to a normal resource or a forum (thread)
                if row['content_key']:
                    page = Page.objects.get(content_id=row['content_key'], is_forum=False, course_offering=self.course_offering)
                else:
                    page = Page.objects.get(content_id=row['forum_key'], is_forum=True, course_offering=self.course_offering)
            except Page.DoesNotExist:
                if row['content_key']:
                    self._add_non_critical_error('Unable to find resource {} for activity'.format(row['content_key']))
                else:
                    self._add_non_critical_error('Unable to find forum {} for activity'.format(row['forum_key']))
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

            batch.append(PageVisit(lms_user=user, page=page, visited_at=visited_at))

            if len(batch) == batch_size:
                try:
                    PageVisit.objects.bulk_create(batch)
                except IntegrityError as e:
                    self._add_error('Integrity Error in activity bulk insert: {}'.format(e))
                batch = []

        try:
            PageVisit.objects.bulk_create(batch)
        except IntegrityError as e:
            self._add_error('Integrity Error in activity bulk insert: {}'.format(e))

    def _process_posts(self, posts_data):
        """
        Extracts posts from the course import files and updates/inserts into the page visits table
        """
        if set(posts_data.fieldnames) != set(self.POSTS_FIELDNAMES):
            raise LMSImportFileError(self.POSTS_FILE, 'Posts data columns do not match {}'.format(self.POSTS_FIELDNAMES))

        for row in posts_data:
            try:
                user = LMSUser.objects.get(lms_user_id=row['user_key'], course_offering=self.course_offering)
            except LMSUser.DoesNotExist:
                self._add_error('Unable to find user {} for post'.format(row['user_key']))
                continue

            values = {
                'title': row['thread'],
                'content_type': self.FORUM_CONTENT_TYPE,
                'parent_id': None,
            }
            page, _ = Page.objects.get_or_create(content_id=row['forum_key'], is_forum=True, course_offering=self.course_offering, defaults=values)

            # In case page was found already, check it's content type to ensure it is a communication type
            if page.content_type not in CourseOffering.communication_types():
                self._add_error('Resource {} for post is not a communication type'.format(page.content_id))
                continue

            try:
                posted_at = dateparse.parse_datetime(row['timestamp'])
                if posted_at is None:
                    self._add_error('Timestamp {} for post is not a valid format'.format(row['timestamp']))
                    continue
            except ValueError:
                self._add_error('Timestamp {} for post is not a valid datetime'.format(row['timestamp']))
                continue

            if posted_at < self.course_offering.start_datetime or posted_at > self.course_offering.end_datetime:
                self._add_non_critical_error('Timestamp {} for post is outside course offering start/end'.format(row['timestamp']))
                continue

            try:
                post = SummaryPost.objects.create(lms_user=user, page=page, posted_at=posted_at)
            except IntegrityError as e:
                self._add_error('Integrity Error in post insert: {}'.format(e))
