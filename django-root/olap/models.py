from django.db import models
from django.db.models.aggregates import Max

from dashboard.models import Course


# CREATE TABLE `summary_courses` (
#   `id` int(11) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `weekly_json` longtext,
#   `users_counts_table` longtext,
#   `users_vis_table` longtext,
#   `access_counts_table` longtext,
#   `access_vis_table` longtext,
#   `content_counts_table` longtext,
#   `content_user_table` longtext,
#   `communication_counts_table` longtext,
#   `communication_user_table` longtext,
#   `assessment_counts_table` longtext,
#   `assessment_user_table` longtext,
#   `content_hiddenlist` longtext,
#   `communication_hiddenlist` longtext,
#   `assessment_hiddenlist` longtext,
#   `forum_posts_table` longtext,
#   `contentcoursepageviews` longtext,
#   `communicationcoursepageviews` longtext,
#   `assessmentcoursepageviews` longtext,
#   `assessmentgrades` longtext,
#   `sitetree` longtext
# ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
# class SummaryCourse(models.Model):
#     course = models.ForeignKey(Course)
#     weekly_json = models.TextField(blank=True)
#     users_counts_table = models.TextField(blank=True)
#     users_vis_table = models.TextField(blank=True)
#     access_counts_table = models.TextField(blank=True)
#     access_vis_table = models.TextField(blank=True)
#     content_counts_table = models.TextField(blank=True)
#     content_user_table = models.TextField(blank=True)
#     communication_counts_table = models.TextField(blank=True)
#     communication_user_table = models.TextField(blank=True)
#     assessment_counts_table = models.TextField(blank=True)
#     assessment_user_table = models.TextField(blank=True)
#     content_hiddenlist = models.TextField(blank=True)
#     communication_hiddenlist = models.TextField(blank=True)
#     assessment_hiddenlist = models.TextField(blank=True)
#     forum_posts_table = models.TextField(blank=True)
#     contentcoursepageviews = models.TextField(blank=True)
#     communicationcoursepageviews = models.TextField(blank=True)
#     assessmentcoursepageviews = models.TextField(blank=True)
#     assessmentgrades = models.TextField(blank=True)
#     sitetree = models.TextField(blank=True)

# CREATE TABLE `dim_users` (
#   `id` int(11) NOT NULL,
#   `lms_id` varchar(1000) NOT NULL,
#   `firstname` varchar(1000) DEFAULT NULL,
#   `lastname` varchar(1000) DEFAULT NULL,
#   `username` varchar(1000) NOT NULL,
#   `role` varchar(1000) DEFAULT NULL,
#   `email` varchar(1000) DEFAULT NULL,
#   `user_pk` varchar(1000) NOT NULL,
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class DimUser(models.Model):
    lms_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    user_pk = models.CharField(max_length=255)  # course_id '_' lms_id
    course = models.ForeignKey(Course)
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = (('course', 'lms_id'), )

    def __str__(self):
        possible_name = " ".join((self.firstname, self.lastname))
        if possible_name:
            return "<DimUser {}: {}>".format(self.lms_id, possible_name)
        else:
            return "<DimUser {}: ## Phantom user ##>".format(self.lms_id)

# CREATE TABLE `fact_coursevisits` (
#   `id` int(11) NOT NULL,
#   `date_id` varchar(1000) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `user_id` int(11) NOT NULL,
#   `page_id` int(11) NOT NULL,
#   `pageview` int(11) NOT NULL DEFAULT '1',
#   `time_id` varchar(1000) NOT NULL,
#   `module` varchar(1000) DEFAULT NULL,
#   `action` varchar(1000) DEFAULT NULL,
#   `url` varchar(5000) DEFAULT NULL,
#   `section_id` int(11) DEFAULT NULL,
#   `datetime` varchar(1000) NOT NULL,
#   `user_pk` varchar(1000) DEFAULT NULL,
#   `page_pk` varchar(1000) DEFAULT NULL,
#   `section_pk` varchar(1000) DEFAULT NULL,
#   `unixtimestamp` varchar(5000) NOT NULL,
#   `section_order` int(11) DEFAULT NULL,
#   `info` varchar(5000) DEFAULT NULL,
#   `session_id` int(11) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class FactCourseVisit(models.Model):
    visited_at = models.DateTimeField()
    course = models.ForeignKey(Course)
    user = models.ForeignKey(DimUser)
    page_id = models.IntegerField()
    pageview = models.IntegerField(default=1)
    module = models.CharField(blank=True, max_length=255)
    action = models.CharField(blank=True, max_length=255)
    url = models.TextField(blank=True)
    section_id = models.IntegerField(blank=True, null=True)
    user_pk = models.CharField(blank=True, max_length=255)
    page_pk = models.CharField(blank=True, max_length=255)
    section_pk = models.CharField(blank=True, max_length=255)
    section_order = models.IntegerField(blank=True, null=True)
    info = models.TextField()
    session_id = models.IntegerField(blank=True, null=True)

# CREATE TABLE `dim_pages` (
#   `id` int(11) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `content_type` varchar(200) NOT NULL,
#   `content_id` int(11) NOT NULL,
#   `parent_id` int(11) NOT NULL,
#   `order_no` int(11) NOT NULL,
#   `title` text NOT NULL,
#   `page_pk` varchar(1000) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

class DimPage(models.Model):
    course = models.ForeignKey(Course)
    content_type = models.CharField(max_length=255)
    content_id = models.IntegerField()
    parent_id = models.IntegerField(default=0)
    order_no = models.IntegerField(default=0)
    title = models.TextField()
    page_pk = models.CharField(max_length=255)

    class Meta:
        unique_together = (('course', 'content_id'), )

    @staticmethod
    def get_next_page_id(course):
        max_page_dict = DimPage.objects.filter(course=course).aggregate(max_page_id=Max('content_id'))
        if max_page_dict['max_page_id']:
            return max_page_dict['max_page_id'] + 1
        return 1

# CREATE TABLE `dim_session` (
#   `id` int(11) NOT NULL,
#   `fact_coursevisits_id` int(11) NOT NULL,
#   `session_id` int(11) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `unixtimestamp` varchar(1000) NOT NULL,
#   `date_id` varchar(11) NOT NULL,
#   `session_length_in_mins` double NOT NULL,
#   `pageviews` int(11) NOT NULL,
#   `date_year` int(11) NOT NULL,
#   `date_week` int(11) NOT NULL,
#   `date_dayinweek` int(11) NOT NULL,
#   `user_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class DimSession(models.Model):
    course = models.ForeignKey(Course)
    session_id = models.IntegerField()
    session_length_in_mins = models.IntegerField()
    pageviews = models.IntegerField()
    first_visit = models.DateTimeField() # Will be replaced with FK to FactCourseVisit

    @staticmethod
    def get_next_session_id():
        max_session_dict = DimSession.objects.all().aggregate(max_session_id=Max('session_id'))
        if max_session_dict['max_session_id']:
            return max_session_dict['max_session_id'] + 1
        return 1

# CREATE TABLE `dim_sessions` (
#   `id` int(11) NOT NULL,
#   `session_id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `Pageviews` int(11) NOT NULL DEFAULT '0',
#   `session_length_in_mins` int(11) NOT NULL,
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
# class DimSessions(models.Model):
#     course = models.ForeignKey(Course)
#     session_id = models.IntegerField()
#     session_length_in_mins = models.IntegerField()
#     pageviews = models.IntegerField(default=0)
#     date_year = models.IntegerField()
#     date_week = models.IntegerField()
#     date_dayinweek = models.IntegerField()

# CREATE TABLE `dim_submissionattempts` (
#   `id` int(11) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `content_id` int(11) NOT NULL,
#   `user_id` int(11) NOT NULL,
#   `grade` varchar(50) NOT NULL,
#   `unixtimestamp` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class DimSubmissionAttempt(models.Model):
    attempted_at = models.DateTimeField()
    course = models.ForeignKey(Course)
    content_id = models.IntegerField()
    user = models.ForeignKey(DimUser)
    grade = models.CharField(max_length=50)


# CREATE TABLE `dim_submissiontypes` (
#   `id` int(11) NOT NULL,
#   `content_type` varchar(1000) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `content_id` int(11) NOT NULL,
#   `timeopen` varchar(1000) NOT NULL,
#   `timeclose` varchar(1000) NOT NULL,
#   `grade` varchar(50) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class DimSubmissionType(models.Model):
    course = models.ForeignKey(Course)
    content_id = models.IntegerField()
    content_type = models.CharField(max_length=255)
    # timeopen = models.DateTimeField() # Hardcoded in importer to 0.  Not needed?
    # timeclose = models.DateTimeField() # Hardcoded in importer to 0.  Not needed?
    grade = models.CharField(max_length=50)


# CREATE TABLE `Summary_CourseAssessmentVisitsByDayInWeek` (
#   `id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Day` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `Pageviews` int(11) NOT NULL DEFAULT '0',
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryCourseAssessmentVisitsByDayInWeek(models.Model):
    date_year = models.IntegerField()
    date_day = models.IntegerField()
    date_week = models.IntegerField()
    date_dayinweek = models.IntegerField()
    pageviews = models.IntegerField(default=0)
    course = models.ForeignKey(Course)


# CREATE TABLE `Summary_CourseCommunicationVisitsByDayInWeek` (
#   `id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Day` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `Pageviews` int(11) NOT NULL DEFAULT '0',
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryCourseCommunicationVisitsByDayInWeek(models.Model):
    date_year = models.IntegerField()
    date_day = models.IntegerField()
    date_week = models.IntegerField()
    date_dayinweek = models.IntegerField()
    pageviews = models.IntegerField(default=0)
    course = models.ForeignKey(Course)


# CREATE TABLE `Summary_CourseVisitsByDayInWeek` (
#   `id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Day` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `Pageviews` int(11) NOT NULL DEFAULT '0',
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryCourseVisitsByDayInWeek(models.Model):
    date_year = models.IntegerField()
    date_day = models.IntegerField()
    date_week = models.IntegerField()
    date_dayinweek = models.IntegerField()
    pageviews = models.IntegerField(default=0)
    course = models.ForeignKey(Course)

# CREATE TABLE `summary_discussion` (
#   `id` int(11) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `forum_id` int(11) NOT NULL,
#   `title` text NOT NULL,
#   `no_posts` int(11) NOT NULL,
#   `sna_json` text NOT NULL,
#   `discussion_id` int(11) NOT NULL,
#   `forum_pk` text NOT NULL,
#   `discussion_pk` text NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryDiscussion(models.Model):
    course = models.ForeignKey(Course)
    forum_id = models.IntegerField()
    title = models.TextField()
    no_posts = models.IntegerField()
    sna_json = models.TextField()
    discussion_id = models.IntegerField()
    forum_pk = models.CharField(max_length=255)
    discussion_pk = models.CharField(max_length=255)


# CREATE TABLE `summary_forum` (
#   `id` int(11) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `forum_id` int(11) NOT NULL,
#   `title` text NOT NULL,
#   `no_discussions` int(11) NOT NULL,
#   `forum_pk` text NOT NULL,
#   `all_content` text NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryForum(models.Model):
    course = models.ForeignKey(Course)
    forum_id = models.IntegerField()
    title = models.TextField()
    no_discussions = models.IntegerField()
    forum_pk = models.CharField(max_length=255)
    all_content = models.TextField()

# CREATE TABLE `Summary_ParticipatingUsersByDayInWeek` (
#   `id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Day` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `Pageviews` int(11) NOT NULL DEFAULT '0',
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryParticipatingUsersByDayInWeek(models.Model):
    date_year = models.IntegerField()
    date_day = models.IntegerField()
    date_week = models.IntegerField()
    date_dayinweek = models.IntegerField()
    pageviews = models.IntegerField(default=0)
    course = models.ForeignKey(Course)


# CREATE TABLE `summary_posts` (
#   `id` int(11) NOT NULL,
#   `date_id` varchar(11) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `forum_id` int(11) NOT NULL,
#   `discussion_id` int(11) NOT NULL,
#   `user_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryPost(models.Model):
    posted_at = models.DateTimeField()
    course = models.ForeignKey(Course)
    forum_id = models.IntegerField()
    discussion_id = models.IntegerField()
    user = models.ForeignKey(DimUser) # Having this is not normalised

# CREATE TABLE `Summary_SessionAverageLengthByDayInWeek` (
#   `id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Day` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `session_average_in_minutes` int(11) NOT NULL DEFAULT '0',
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummarySessionAverageLengthByDayInWeek(models.Model):
    date_year = models.IntegerField()
    date_week = models.IntegerField()
    date_dayinweek = models.IntegerField()
    session_average_in_minutes = models.IntegerField(default=0)
    course = models.ForeignKey(Course)


# CREATE TABLE `Summary_SessionAveragePagesPerSessionByDayInWeek` (
#   `id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Day` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `pages_per_session` int(11) NOT NULL DEFAULT '0',
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummarySessionAveragePagesPerSessionByDayInWeek(models.Model):
    date_year = models.IntegerField()
    date_week = models.IntegerField()
    date_dayinweek = models.IntegerField()
    pages_per_session = models.IntegerField(default=0)
    course = models.ForeignKey(Course)


# CREATE TABLE `Summary_SessionsByDayInWeek` (
#   `id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Day` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `Sessions` int(11) NOT NULL DEFAULT '0',
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummarySessionsByDayInWeek(models.Model):
    date_year = models.IntegerField()
    date_week = models.IntegerField()
    date_dayinweek = models.IntegerField()
    sessions = models.IntegerField(default=0)
    course = models.ForeignKey(Course)

# CREATE TABLE `Summary_UniquePageViewsByDayInWeek` (
#   `id` int(11) NOT NULL,
#   `Date_Year` int(11) NOT NULL,
#   `Date_Day` int(11) NOT NULL,
#   `Date_Week` int(11) NOT NULL,
#   `Date_dayinweek` int(11) NOT NULL,
#   `Pageviews` int(11) NOT NULL DEFAULT '0',
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryUniquePageViewsByDayInWeek(models.Model):
    date_year = models.IntegerField()
    date_day = models.IntegerField()
    date_week = models.IntegerField()
    date_dayinweek = models.IntegerField()
    pageviews = models.IntegerField(default=0)
    course = models.ForeignKey(Course)
