import csv
import datetime

from django.conf import settings
import unicodedata

from django.db import connection
from unipath.path import Path
import xml.etree.cElementTree as ET

from dashboard.models import Course
from olap.models import DimDate
from olap.models import DimPage
from olap.models import DimSession
from olap.models import DimSubmissionAttempt
from olap.models import DimSubmissionType
from olap.models import DimUser
from olap.models import FactCourseVisit
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


class ImportLmsData(object):
    SESSION_LENGTH_MINS = 40

    staff_list = []
    sitetree = {}

    def __init__(self):
        self.courses_export_path = Path(settings.PROJECT_DIR, 'data')

    def process(self):
        print("Removing old data")
        self.remove_olap_data()

        print('Generating dates')
        self._generate_dates()

        for course in Course.objects.all():
            if course.lms_type == Course.LMS_TYPE_BLACKBOARD:
                print("Importing course data for {}".format(course))
                lms_import = BlackboardImport(self.courses_export_path, course)
                lms_import.process_import_data()

                print("Processing user sessions for {}".format(course))
                self._process_user_sessions(course)

                print("Populating summary data for {}".format(course))
                self._populate_summary_tables(course, lms_import.get_assessment_types(), lms_import.get_communication_types())

    def remove_olap_data(self):
        # First the OLAP Tables
        DimDate.objects.all().delete()
        DimUser.objects.all().delete()
        DimPage.objects.all().delete()
        FactCourseVisit.objects.all().delete()
        DimSession.objects.all().delete()
        DimSubmissionAttempt.objects.all().delete()
        DimSubmissionType.objects.all().delete()

        # # Next cleanup the Summary Tables
        # connection.execute("DELETE FROM Summary_Courses");
        SummaryForum.objects.all().delete()
        SummaryDiscussion.objects.all().delete()
        SummaryPost.objects.all().delete()
        SummaryCourseVisitsByDayInWeek.objects.all().delete()
        SummaryCourseCommunicationVisitsByDayInWeek.objects.all().delete()
        SummaryCourseAssessmentVisitsByDayInWeek.objects.all().delete()
        SummarySessionsByDayInWeek.objects.all().delete()
        SummarySessionAverageLengthByDayInWeek.objects.all().delete()
        SummarySessionAveragePagesPerSessionByDayInWeek.objects.all().delete()
        SummaryParticipatingUsersByDayInWeek.objects.all().delete()
        SummaryUniquePageViewsByDayInWeek.objects.all().delete()

    def _store_session(self, course, user, session_id, session_visits_list):
        if session_visits_list:
            first_visit = session_visits_list[0]
            last_visit = session_visits_list[len(session_visits_list)-1]
            session_start = datetime.datetime.fromtimestamp(first_visit.unixtimestamp)
            session_end = datetime.datetime.fromtimestamp(last_visit.unixtimestamp)
            session_duration = (session_end - session_start).seconds / 60
            page_views = len(session_visits_list)
            date_year = session_start.year
            date_week = session_start.isocalendar()[1]
            date_dayinweek = session_start.weekday()
            dim_session = DimSession(user_id=user.lms_id, date_week=date_week, date_year=date_year,
                                     date_dayinweek=date_dayinweek, pageviews=page_views, session_length_in_mins=session_duration,
                                     session_id=session_id, course=course, unixtimestamp=first_visit.unixtimestamp, date_id=first_visit.date_id)
            dim_session.save()
            session_visits_list_ids = [v.id for v in session_visits_list]
            FactCourseVisit.objects.filter(id__in=session_visits_list_ids).update(session_id=session_id)

    def _process_user_sessions(self, course):
        """
            Gets each user (i.e., student) and calls method to process to split visits into a session.
            A session includes all pageviews where the time access difference does not exceed SESSION_LENGTH_MINS
            Algorithm to Determine Sessions:
                get all visits for a user in order
                loop through all visits for the user
                    group visits into blocks of SESSION_LENGTH_MINS
                    create a session record for each block (timestamped with start of session)
                    update all visits in the block with the corresponding session_id
        """
        users = DimUser.objects.filter(course=course)

        for user in users:
            visits = FactCourseVisit.objects.filter(user_id=user.lms_id).order_by('unixtimestamp')
            session_id = DimSession.get_next_session_id()

            session_start = None
            session_visits_list = []
            for visit in visits:
                if session_start is None:
                    session_start = datetime.datetime.fromtimestamp(visit.unixtimestamp)
                    session_visits_list = [visit]
                    continue

                session_end = datetime.datetime.fromtimestamp(visit.unixtimestamp)

                session_duration = (session_end - session_start).seconds / 60
                if session_duration >= self.SESSION_LENGTH_MINS:
                    self._store_session(course, user, session_id, session_visits_list)
                    session_id += 1
                    session_start = session_end
                    session_visits_list = [visit]
                else:
                    session_visits_list.append(visit)

            self._store_session(course, user, session_id, session_visits_list)

    def _populate_summary_tables(self, course, assessment_types, communication_types):
        """
            Produces summary tables Summary_CourseVisitsByDayInWeek, Summary_CourseCommunicationVisitsByDayInWeek
            Summary_CourseAssessmentVisitsByDayInWeek, Summary_SessionAverageLengthByDayInWeek, Summary_SessionAveragePagesPerSessionByDayInWeek
            Summary_ParticipatingUsersByDayInWeek, Summary_UniquePageViewsByDayInWeek
        """

        excluded_content_types = communication_types + assessment_types
        course_weeks = course.get_weeks()
        excluded_types_placeholders = ",".join(['%s' for s in excluded_content_types])
        communication_types_placeholders = ','.join("%s" for s in communication_types)
        assessment_types_placeholders = ','.join("%s" for s in assessment_types)

        # Populate Summary_CourseVisitsByDayInWeek - only contains content items
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, SUM(F.pageview) AS pageviews, F.course_id FROM olap_dimdate D LEFT JOIN olap_factcoursevisit F ON D.id = F.date_id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s AND F.module NOT IN ({}) GROUP BY D.date_week, D.date_dayinweek".format(excluded_types_placeholders)
            cursor.execute(sql, [course_weeks, course.id] + excluded_content_types)
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryCourseVisitsByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course=course)
                summary.save()

        # Populate Summary_CourseCommunicationVisitsByDayInWeek - only contains forums
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, SUM(F.pageview) AS pageviews, F.course_id FROM olap_dimdate D LEFT JOIN olap_factcoursevisit F ON D.id = F.date_id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s AND F.module IN ({}) GROUP BY D.date_week, D.date_dayinweek".format(communication_types_placeholders)
            cursor.execute(sql, [course_weeks, course.id] + communication_types)
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryCourseCommunicationVisitsByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course=course)
                summary.save()

        # Populate Summary_CourseAssessmentVisitsByDayInWeek - only contains quiz and assign
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, SUM(F.pageview) AS pageviews, F.course_id FROM olap_dimdate D LEFT JOIN olap_factcoursevisit F ON D.id = F.date_id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s AND F.module IN ({}) GROUP BY D.date_week, D.date_dayinweek".format(assessment_types_placeholders)
            cursor.execute(sql, [course_weeks, course.id] + assessment_types)
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryCourseAssessmentVisitsByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course=course)
                summary.save()

        # Populate Summary_SessionAverageLengthByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT S.date_year, S.date_week, S.date_dayinweek, AVG(S.session_length_in_mins), S.course_id FROM olap_dimsession S WHERE S.date_dayinweek IN (0,1,2,3,4,5,6) AND S.date_week IN %s AND S.course_id=%s GROUP BY S.date_week, S.date_dayinweek"
            cursor.execute(sql, [course_weeks, course.id])
            results = cursor.fetchall()
            for row in results:
                session_average_in_minutes = row[3] if row[3] is not None else 0
                summary = SummarySessionAverageLengthByDayInWeek(date_year=row[0], date_week=row[1], date_dayinweek=row[2], session_average_in_minutes=session_average_in_minutes, course=course)
                summary.save()

        # Populate Summary_SessionAveragePagesPerSessionByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT S.date_year, S.date_week, S.date_dayinweek, AVG(S.pageviews), S.course_id FROM olap_dimsession S WHERE S.date_dayinweek IN (0,1,2,3,4,5,6) AND S.date_week IN %s AND S.course_id=%s GROUP BY S.date_week, S.date_dayinweek"
            cursor.execute(sql, [course_weeks, course.id])
            results = cursor.fetchall()
            for row in results:
                pages_per_session = row[3] if row[3] is not None else 0
                summary = SummarySessionAveragePagesPerSessionByDayInWeek(date_year=row[0], date_week=row[1], date_dayinweek=row[2], pages_per_session=pages_per_session, course=course)
                summary.save()

        # Populate Summary_SessionsByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT S.date_year, S.date_week, S.date_dayinweek, COUNT(DISTINCT S.session_id), S.course_id FROM olap_dimsession S WHERE S.date_dayinweek IN (0,1,2,3,4,5,6) AND S.date_week IN %s AND S.course_id=%s GROUP BY S.date_week, S.date_dayinweek"
            cursor.execute(sql, [course_weeks, course.id])
            results = cursor.fetchall()
            for row in results:
                sessions = row[3] if row[3] is not None else 0
                summary = SummarySessionsByDayInWeek(date_year=row[0], date_week=row[1], date_dayinweek=row[2], sessions=sessions, course=course)
                summary.save()

        # Populate Summary_ParticipatingUsersByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, SUM(F.pageview), F.course_id FROM olap_dimdate D LEFT JOIN olap_factcoursevisit F ON D.id = F.date_id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s GROUP BY D.date_week, D.date_dayinweek;"
            cursor.execute(sql, [course_weeks, course.id])
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryParticipatingUsersByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course=course)
                summary.save()

        # Populate Summary_UniquePageViewsByDayInWeek
        with connection.cursor() as cursor:
            sql = "SELECT D.date_year, D.date_day, D.date_week, D.date_dayinweek, COUNT(DISTINCT F.page_id), F.course_id FROM olap_factcoursevisit F INNER JOIN olap_dimdate D ON F.date_id = D.id WHERE D.date_dayinweek IN (0,1,2,3,4,5,6) AND D.date_week IN %s AND F.course_id=%s GROUP BY D.date_week, D.date_dayinweek"
            cursor.execute(sql, [course_weeks, course.id])
            results = cursor.fetchall()
            for row in results:
                pageview = row[4] if row[4] is not None else 0
                summary = SummaryUniquePageViewsByDayInWeek(date_year=row[0], date_day=row[1], date_week=row[2], date_dayinweek=row[3], pageviews=pageview, course=course)
                summary.save()


    def _generate_dates(self):
        """
            Generates dates for the date dimension table
        """
        start_date =  datetime.datetime.strptime("1-JAN-14", "%d-%b-%y")
        end_date =  datetime.datetime.strptime("31-DEC-16", "%d-%b-%y")

        cur_date = start_date
        while cur_date <= end_date:
            self._insert_date(cur_date)
            cur_date = cur_date + datetime.timedelta(days=1)

    def _insert_date(self, date_val: datetime):
        """
        Inserts a date in the dim_dates dimension table

        Args:
            year: 4 digit year
            month: 1 - 12 month value
            day: day of the month
            dayinweek: 0 - 6 day in week
            week: week in year value

        Returns:
            id of the inserted date
        """
        if date_val:
            date_obj = DimDate(
                id=datetime.datetime.strftime(date_val, "%d-%b-%y"),
                date_year=date_val.year,
                date_month=date_val.month,
                date_day=date_val.day,
                date_dayinweek=date_val.weekday(),
                date_week=date_val.isocalendar()[1],
                unixtimestamp=date_val.timestamp(),
            )

            if date_obj.date_month == 12 and date_obj.date_week <= 1:
                date_obj.date_week = 52
            if date_obj.date_month == 1 and date_obj.date_week >= 52:
                date_obj.date_week = 1

            date_obj.save()


class BaseLmsImport(object):

    def __init__(self, courses_export_path, course):
        self.course = course
        self.course_export_path = Path(courses_export_path, course.id)

    def process_import_data(self):
        raise NotImplementedError("'process_import_data' must be implemented")

    def get_assessment_types(self):
        raise NotImplementedError("'get_assessment_types' must be implemented")

    def get_communication_types(self):
        raise NotImplementedError("'get_communication_types' must be implemented")




class BlackboardImport(BaseLmsImport):
    announcements_id = None
    gradebook_id = None
    user_membership_resource_file = None
    resource_id_type_lookup_dict = {}
    content_link_id_to_content_id_dict = {}

    def get_assessment_types(self):
        return ['assessment/x-bb-qti-test', 'course/x-bb-courseassessment', 'resource/x-turnitin-assignment']

    def get_communication_types(self):
        return ['resource/x-bb-discussionboard', 'course/x-bb-collabsession', 'resource/x-bb-discussionfolder']

    def process_import_data(self):
        self._process_manifest()
        self._process_users()
        self._process_access_log()

    def _process_manifest(self):
        manifest_file = Path(self.course_export_path, 'imsmanifest.xml')
        tree = ET.ElementTree(file=manifest_file)
        root = tree.getroot()

        membership_file = None
        gradebook_file = None

        # Get all resource no and the pk for each.
        # Store a dict to map resource no to pk and a dict of counts of content types
        # Make a dict to match resource no to pk (id)
        resource_pk_dict = {}
        resource_type_lookup_dict = {}
        resource_name_lookup_dict = {}
        toc_dict = {'discussion_board_entry': 0, 'staff_information': 0, 'announcements_entry': 0, 'check_grade': 0}

        # Make a dict to store counts of content types
        resource_type_dict = {}

        assessment_res_to_id_dict = {}

        for elem in tree.iter(tag='resource'):
            resource_file = elem.attrib["{http://www.blackboard.com/content-packaging/}file"]
            resource_file_path = Path(self.course_export_path, resource_file)

            # http://www.peterbe.com/plog/unicode-to-ascii
            resource_title = elem.attrib["{http://www.blackboard.com/content-packaging/}title"]
            resource_title = unicodedata.normalize('NFKD', resource_title).encode('ascii', 'ignore')

            resource_type = elem.attrib["type"]
            if resource_type == "resource/x-bb-document":
                resource_type = self._get_resource_content_type(resource_file_path)
            resource_no = elem.attrib["{http://www.w3.org/XML/1998/namespace}base"]
            # the type file has invalid xml course/x-bb-trackingevent so ignore

            real_id = "0"
            if resource_type not in ["course/x-bb-trackingevent", "assessment/x-bb-qti-attempt", "resource/x-bb-announcement"]:
                resource_id = self._get_resource_id(resource_file_path, resource_type)

                resource_pk_dict[resource_no] = resource_id
                resource_type_lookup_dict[resource_no] = resource_type
                resource_name_lookup_dict[resource_no] = resource_title
                if resource_id != '0':
                    self.resource_id_type_lookup_dict[resource_id[1:len(resource_id) - 2]] = resource_type
                    real_id = resource_id[1:-2]
                else:
                    self.resource_id_type_lookup_dict[resource_id] = resource_type
                if resource_type in resource_type_dict:
                    resource_type_dict[resource_type] = resource_type_dict[resource_type] + 1
                else:
                    resource_type_dict[resource_type] = 1
                if resource_type == "course/x-bb-user":
                    self.user_membership_resource_file = resource_file_path

                if resource_type == "resource/x-bb-discussionboard":
                    self._process_forum(resource_file_path)
                elif resource_type == "resource/x-bb-conference":
                    self._process_conferences(resource_file_path, resource_id)
                elif resource_type == "course/x-bb-gradebook":
                    gradebook_file = resource_file
                elif resource_type == "assessment/x-bb-qti-test":
                    self._process_exam(resource_file_path, resource_id, resource_type)
                    assessment_res_to_id_dict[resource_no] = resource_id[1:-2]
                elif resource_type == 'membership/x-bb-coursemembership':
                    membership_file = resource_file

                if resource_type in ['assessment/x-bb-qti-test', 'resource/x-bb-discussionboard']:
                    dim_page = DimPage(course=self.course, content_type=resource_type, content_id=real_id, title=resource_title)
                    dim_page.save()

        parent_map = {}
        for parent_node in tree.iter():
            for child_node in parent_node:
                parent_map[child_node] = parent_node

        order = 1
        for node in parent_map:
            if node.tag == "item" and 'identifierref' in node.attrib:
                current_node = node.attrib["identifierref"]
                parent_node = parent_map[node]
                if parent_node.tag == "organization":
                    parent_resource = parent_node.attrib["identifier"]
                    if parent_resource in resource_pk_dict:
                        parent_resource_no = resource_pk_dict[parent_resource]
                    else:
                        parent_resource_no = 0
                elif 'identifierref' in parent_node.attrib:
                    parent_resource = parent_node.attrib["identifierref"]
                    if parent_resource in resource_pk_dict:
                        parent_resource_no = resource_pk_dict[parent_resource]
                    else:
                        parent_resource_no = 0
                else:
                    parent_resource_no = 0
                current_node_name = resource_name_lookup_dict[current_node]  # node.attrib["{http://www.blackboard.com/content-packaging/}title"]
                current_node_type = resource_type_lookup_dict[current_node]
                current_node_id = resource_pk_dict[current_node]
                current_node_id = current_node_id[1:len(current_node_id) - 2]
                if parent_resource_no != 0:
                    parent_resource_no = parent_resource_no[1:len(parent_resource_no) - 2]

                # get actual content handle
                content_handle = self._get_content_handle(Path(self.course_export_path, current_node + ".dat"))

                if content_handle in toc_dict:
                    toc_dict[content_handle] = current_node_id
                    if content_handle == "staff_information":
                        current_node_type = "resource/x-bb-stafffolder"
                    elif content_handle == "discussion_board_entry":
                        current_node_type = "resource/x-bb-discussionfolder"
                    elif content_handle == "check_grade":
                        current_node_type = "course/x-bb-gradebook"

                if current_node_type != "resource/x-bb-asmt-test-link":
                    dim_page = DimPage(course=self.course, content_type=current_node_type, content_id=current_node_id, title=current_node_name, order_no=order, parent_id=parent_resource_no)
                    dim_page.save()
            order += 1

        # store single announcements item to match announcements coming from log
        self.announcements_id = DimPage.get_next_page_id(self.course)
        announcements_page = DimPage(course=self.course, content_type="resource/x-bb-announcement", content_id=self.announcements_id, title="Announcements")
        announcements_page.save()

        # store single view gradebook to match check_gradebook coming from log
        self.gradebook_id = DimPage.get_next_page_id(self.course)
        gradebook_page = DimPage(course=self.course, content_type="course/x-bb-gradebook", content_id=self.gradebook_id, title="View Gradebook")
        gradebook_page.save()

        # remap /x-bbstaffinfo and discussion boards
        if toc_dict['staff_information'] != 0:
            DimPage.objects.filter(course=self.course, content_type="resource/x-bb-staffinfo").update(parent_id=toc_dict['staff_information'])

        # process memberships
        member_to_user_dict = self._process_memberships(Path(self.course_export_path, membership_file))

        # process quiz attempts in gradebook file
        self._process_attempts(Path(self.course_export_path, gradebook_file), assessment_res_to_id_dict, member_to_user_dict, self.course_export_path)

    def _process_users(self):
        """
        Extracts users from the course export files and inserts into the dim_users table
        Todo: Update to include all roles not only students
        """
        tree = ET.ElementTree(file=self.user_membership_resource_file)
        root = tree.getroot()
        username = None
        firstname = None
        lastname = None
        role = None
        email = None
        for child_of_root in root:
            user_id = str(child_of_root.attrib["id"])
            user_id = user_id[1:(len(user_id) - 2)]
            for child_child_of_root in child_of_root:
                if child_child_of_root.tag == "EMAILADDRESS":
                    email = child_child_of_root.attrib["value"]
                if child_child_of_root.tag == "USERNAME":
                    username = child_child_of_root.attrib["value"]
                for child_child_child_of_root in child_child_of_root:
                    if child_child_child_of_root.tag == "GIVEN":
                        firstname = child_child_child_of_root.attrib["value"]
                        firstname = firstname.replace("'", "''")
                    elif child_child_child_of_root.tag == "FAMILY":
                        lastname = child_child_child_of_root.attrib["value"]
                        lastname = lastname.replace("'", "''")
                    elif child_child_child_of_root.tag == "ROLEID":
                        role = child_child_child_of_root.attrib["value"]

            user_pk = str(self.course.id) + "_" + user_id
            if not firstname:
                firstname = "blank"
            if not lastname:
                lastname = "blank"
            if not email:
                email = "blank"
            if role != "STAFF":
                user = DimUser(lms_id=user_id, firstname=firstname, lastname=lastname, username=username, email=email, role=role, user_pk=user_pk, course=self.course)
                user.save()

    def _process_access_log(self):
        """
            Extract entries from the csv log file from a Blackboard course and inserts each entry as a row in the fact_coursevisits table
        """
        course_log_file = Path(self.course_export_path, 'log.csv')
        with open(course_log_file, 'rU') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Process row
                cur_visit_date = datetime.datetime.strptime(row["TIMESTAMP"], "%d-%b-%y %H:%M:%S")  # eg 01-SEP-14 09:46:52
                date_id = datetime.datetime.strftime(cur_visit_date, "%d-%b-%y")  # time.strftime("%d-%b-%y", cur_visit_date)
                time_id = datetime.datetime.strftime(cur_visit_date, "%H:%M:%S")  # time.strftime("%H:%M:%S", cur_visit_date)

                unixtimestamp = cur_visit_date.timestamp()

                user_id = row["USER_PK1"]
                page_id = row["CONTENT_PK1"]
                action = row["EVENT_TYPE"]
                forum_id = row["FORUM_PK1"]

                if forum_id:
                    page_id = forum_id

                # default for module
                content_type = "blank"
                if page_id:
                    if str(page_id) in self.resource_id_type_lookup_dict:
                        content_type = self.resource_id_type_lookup_dict[str(page_id)]
                    else:
                        if not row["INTERNAL_HANDLE"]:
                            content_type = row["DATA"]
                            # also add to dim_pages
                            if not DimPage.objects.filter(content_id=int(page_id)).exists():
                                title = "blank"
                                if content_type == "/webapps/blackboard/execute/blti/launchLink":
                                    title = "LTI Link"
                                elif content_type == "/webapps/blackboard/execute/manageCourseItem":
                                    title = "Manage Course Item"
                                dim_page = DimPage(course=self.course, content_type=content_type, content_id=page_id, title=title)
                                dim_page.save()
                elif row["INTERNAL_HANDLE"] == "my_announcements":
                    content_type = "resource/x-bb-announcement"
                    page_id = str(self.announcements_id)
                elif row["INTERNAL_HANDLE"] == "check_grade":
                    content_type = "course/x-bb-gradebook"
                    page_id = str(self.gradebook_id)

                user_pk = str(self.course.id) + "_" + user_id
                page_pk = str(self.course.id) + "_" + page_id

                # map all links in content to assessment to actual assessment id
                if page_id in self.content_link_id_to_content_id_dict:
                    page_id = self.content_link_id_to_content_id_dict[page_id]

                # Need to exclude forum post creation as this is counted in summary_posts
                # Exclude admin actions such as entering an announcement
                if row["INTERNAL_HANDLE"] not in ['discussion_board_entry', 'db_thread_list_entry',
                                                   'db_collection_entry', 'announcements_entry',
                                                   'cp_gradebook_needs_grading']:
                    if not page_id:
                        page_id = 0
                    fact_visit = FactCourseVisit(date_id=date_id, time_id=time_id, course=self.course, user_id=user_id, module=content_type, action=action, page_id=page_id, user_pk=user_pk, page_pk=page_pk, unixtimestamp=unixtimestamp)
                    fact_visit.save()

    def _get_resource_content_type(self, file_path):
        tree = ET.ElementTree(file=file_path)
        root = tree.getroot()
        content_type = ""
        for elem in tree.iter(tag='CONTENTHANDLER'):
            content_type =  elem.attrib["value"]
        return content_type

    def _get_resource_id(self, resource_file, resource_type=None):
        resource_id = '0'
        tree = ET.ElementTree(file=resource_file)
        root = tree.getroot()
        if resource_type == "assessment/x-bb-qti-test":
            for elem in tree.iter(tag='assessmentmetadata'):
                for elem_elem in elem:
                    if elem_elem.tag == "bbmd_asi_object_id":
                        resource_id =  elem_elem.text
        else:
            if "id" in root.attrib:
                resource_id = root.attrib["id"]
            elif root.tag == "questestinterop":
                for elem in tree.iter(tag='assessmentmetadata'):
                    for elem_elem in elem:
                        if elem_elem.tag == "bbmd_asi_object_id":
                            resource_id =  elem_elem.text
            else:
                resource_id = '0'

        return resource_id

    def _get_content_handle(self, file_path):
        tree = ET.ElementTree(file=file_path)
        root = tree.getroot()
        content_handle = ""
        for elem in tree.iter(tag='INTERNALHANDLE'):
            content_handle = elem.attrib["value"]
        return content_handle

    def _process_forum(self, file_path):
        tree = ET.ElementTree(file=file_path)
        root = tree.getroot()
        forum_id = root.attrib['id']
        forum_id = forum_id[1:len(forum_id) - 2]
        conference_id = ""
        for elem in root:
            if elem.tag == "CONFERENCEID":
                conference_id = elem.attrib["value"]
                conference_id = conference_id[1:len(conference_id) - 2]

        # Get all posts
        for msg in tree.iter(tag='MSG'):
            date_id = ""
            user_id = ""
            for elem in msg:
                if elem.tag == "USERID":
                    user_id = elem.attrib["value"]
                for subelem in elem:
                    if subelem.tag == "CREATED":
                        date_id = subelem.attrib["value"]

            if (date_id is not None) and (len(date_id) != 0) and (date_id != " ") and (date_id != ""):
                date_id = date_id[0:len(date_id) - 4]
                post_date = datetime.datetime.strptime(date_id, "%Y-%m-%d %H:%M:%S")  # 2014-07-11 16:52:53 EST
                date_id = datetime.datetime.strftime(post_date, "%d-%b-%y")
                user_id = user_id[1:len(user_id) - 2]
                post = SummaryPost(date_id=date_id, user_id=user_id, course=self.course, forum_id=forum_id, discussion_id=conference_id)
                post.save()

    def _process_conferences(self, file_path, content_id):
        forum = SummaryForum(course=self.course, forum_id=content_id, title='Conferences', no_discussions=0)
        forum.save()

        tree = ET.ElementTree(file=file_path)
        root = tree.getroot()

        title = ""
        for elem in tree.iter(tag='CONFERENCE'):
            conference_id = elem.attrib["id"]
            conference_id = conference_id[1:len(conference_id) - 2]
            for child_of_root in elem:
                if child_of_root.tag == "TITLE":
                    title = child_of_root.attrib["value"]

            discussion = SummaryDiscussion(course=self.course, forum_id=conference_id, discussion_id=content_id, title=title, no_posts=0)
            discussion.save()

    def _process_exam(self, file_path, content_id, content_type):
        timeopen = 0
        timeclose = 0
        grade = 0.0
        content_id = content_id[1:-2]
        tree = ET.ElementTree(file=file_path)
        root = tree.getroot()
        for elem in tree.iter(tag='qmd_absolutescore_max'):
            grade = elem.text

        submission_type = DimSubmissionType(course=self.course, content_id=content_id, content_type=content_type, timeopen=timeopen, timeclose=timeclose, grade=grade)
        submission_type.save()

    def _process_memberships(self, file_path):
        tree = ET.ElementTree(file=file_path)
        root = tree.getroot()
        member_to_user_dict = {}
        for elem in tree.iter(tag='COURSEMEMBERSHIP'):
            member_id = elem.attrib["id"]
            member_id = member_id[1:-2]
            user_id = 0
            for usr in elem:
                if usr.tag == "USERID":
                    user_id = usr.attrib["value"]
                    user_id = user_id[1:-2]
            member_to_user_dict[member_id] = user_id
        return member_to_user_dict

    def _process_attempts(self, file_path, assessment_res_to_id_dict, member_to_user_dict, path):
        tree = ET.ElementTree(file=file_path)
        root = tree.getroot()
        content_id = None  # content_id[1:-2]
        content_link_id = None
        for elem in tree.iter(tag='OUTCOMEDEFINITION'):
            for child_of_root in elem:
                # This is the OUTCOMEDEFINITION level
                if child_of_root.tag == "ASIDATAID":
                    resource_id = child_of_root.attrib['value']
                    if resource_id in assessment_res_to_id_dict:
                        content_id = assessment_res_to_id_dict[resource_id]
                if child_of_root.tag == "CONTENTID":
                    resource_link = child_of_root.attrib['value']
                    if resource_link== "":
                        content_link_id = None
                    else:
                        link_id = self._get_resource_id(Path(path, resource_link + ".dat"))
                        content_link_id = link_id[1:-2]
                if child_of_root.tag == "EXTERNALREF":
                    external_ref = child_of_root.attrib['value']
                    if content_id is None and external_ref != "":
                        content_id = external_ref[1:-2]
                for child_child_of_root in child_of_root:
                    # This is the outcomes level
                    user_id = None
                    grade = None
                    date_str = None
                    for child_child_child_of_root in child_child_of_root:
                        if child_child_child_of_root.tag == "COURSEMEMBERSHIPID":
                            member_id = child_child_child_of_root.attrib["value"]
                            member_id = member_id[1:len(member_id) - 2]
                            if member_id in member_to_user_dict:
                                user_id = member_to_user_dict[member_id]
                            else:
                                user_id = member_id

                        for child_child_child_child_of_root in child_child_child_of_root:

                            for child_child_child_child_child_of_root in child_child_child_child_of_root:

                                if child_child_child_child_child_of_root.tag == "SCORE":
                                    grade = child_child_child_child_child_of_root.attrib['value']
                                if child_child_child_child_child_of_root.tag == "DATEATTEMPTED":
                                    date_str = child_child_child_child_child_of_root.attrib['value']

                    if content_id is not None and grade is not None:  # i.e. 0 attempts -
                        date_str = date_str[0:len(date_str) - 4]        # 2014-07-11 16:52:53 EST
                        post_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

                        unixtimestamp = post_date.timestamp()

                        date_id = datetime.datetime.strftime(post_date, "%d-%b-%y")
                        time_id = datetime.datetime.strftime(post_date, "%H:%M:%S")

                        attempt = DimSubmissionAttempt(course=self.course, content_id=content_id, grade=grade, user_id=user_id, unixtimestamp=unixtimestamp)
                        attempt.save()

                        if content_link_id is not None:
                            self.content_link_id_to_content_id_dict[content_link_id] = content_id

                        # save all attempts as pageviews in fact_coursevisits
                        user_pk = str(self.course.id) + "_" + user_id
                        page_pk = str(self.course.id) + "_" + content_id

                        fact_visit = FactCourseVisit(date_id=date_id, time_id=time_id, course=self.course,
                                    user_id=user_id, module='assessment/x-bb-qti-test', action='COURSE_ACCESS', page_id=content_id, pageview=1, user_pk=user_pk,
                                                     page_pk=page_pk, unixtimestamp=unixtimestamp)
                        fact_visit.save()
