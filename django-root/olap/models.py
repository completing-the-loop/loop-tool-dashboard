from django.db import models
from django.db.models.aggregates import Max

from dashboard.models import CourseOffering


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
#     course_offering = models.ForeignKey(CourseOffering)
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
#   `lms_user_id` varchar(1000) NOT NULL,
#   `firstname` varchar(1000) DEFAULT NULL,
#   `lastname` varchar(1000) DEFAULT NULL,
#   `username` varchar(1000) NOT NULL,
#   `role` varchar(1000) DEFAULT NULL,
#   `email` varchar(1000) DEFAULT NULL,
#   `user_pk` varchar(1000) NOT NULL,
#   `course_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class LMSUser(models.Model):
    lms_user_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    course_offering = models.ForeignKey(CourseOffering)
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, blank=True)

    class Meta:
        unique_together = (('course_offering', 'lms_user_id'), )

    def __str__(self):
        possible_name = " ".join((self.firstname, self.lastname))
        if possible_name:
            return "<LMSUser {}: {}>".format(self.lms_user_id, possible_name)
        else:
            return "<LMSUser {}: ## Phantom user ##>".format(self.lms_user_id)

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
class PageVisit(models.Model):
    lms_activity_id = models.CharField(max_length=255)
    visited_at = models.DateTimeField()
    lms_user = models.ForeignKey(LMSUser)
    page = models.ForeignKey('Page')
    session = models.ForeignKey('LMSSession', blank=True, null=True) # We need to allow blank to cater for period before sessions are calculated.

    class Meta:
        unique_together = (('lms_user', 'page', 'visited_at'), )

    # TODO: There's several fields here which are candidates for removal/alteration.  Audit.
    module = models.CharField(blank=True, max_length=255) # Is this always a resource/x-bb-* content type?
    action = models.CharField(blank=True, max_length=255)
    url = models.TextField(blank=True)
    section_id = models.IntegerField(blank=True, null=True)
    section_pk = models.CharField(blank=True, max_length=255)
    section_order = models.IntegerField(blank=True, null=True)
    info = models.TextField()

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

class Page(models.Model):
    course_offering = models.ForeignKey(CourseOffering)
    content_type = models.CharField(max_length=255)
    content_id = models.IntegerField()
    is_forum = models.BooleanField(default=False)   # Defines whether content_id is from the resources or the forums
    parent = models.ForeignKey('self', null=True, blank=True)
    order_no = models.IntegerField(default=0)
    title = models.TextField()

    class Meta:
        unique_together = (('course_offering', 'content_id', 'is_forum'), )

    def __str__(self):
        return '<Page {}: {}>'.format(self.id, self.title)

    @staticmethod
    def get_next_page_id(course_offering):
        max_page_dict = Page.objects.filter(course_offering=course_offering).aggregate(max_page_id=Max('content_id'))
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
class LMSSession(models.Model):
    # Not strictly needed (since we can find course_offering by .first_visit.page.course_offering, but it will make queries easier.
    course_offering = models.ForeignKey(CourseOffering)
    session_length_in_mins = models.IntegerField()
    pageviews = models.IntegerField()
    first_visit = models.ForeignKey(PageVisit)

    """
    @staticmethod
    def get_next_session_id():
        max_session_dict = LMSSession.objects.all().aggregate(max_session_id=Max('session_id'))
        if max_session_dict['max_session_id']:
            return max_session_dict['max_session_id'] + 1
        return 1
    """

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
#     course_offering = models.ForeignKey(CourseOffering)
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
class SubmissionAttempt(models.Model):
    attempt_key = models.CharField(max_length=255)
    attempted_at = models.DateTimeField()
    page = models.ForeignKey(Page) # Was called content_id
    lms_user = models.ForeignKey(LMSUser)
    grade = models.CharField(max_length=50)

    class Meta:
        unique_together = (('lms_user', 'page', 'attempted_at'),)


# CREATE TABLE `dim_submissiontypes` (
#   `id` int(11) NOT NULL,
#   `content_type` varchar(1000) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `content_id` int(11) NOT NULL,
#   `timeopen` varchar(1000) NOT NULL,
#   `timeclose` varchar(1000) NOT NULL,
#   `grade` varchar(50) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SubmissionType(models.Model):
    course_offering = models.ForeignKey(CourseOffering)
    content_id = models.IntegerField() # This should be an FK to Page, but we can't replace it yet because the importer tries to create DimSubmissionAttempts before Pages.
    content_type = models.CharField(max_length=255)
    grade = models.DecimalField(max_digits=7, decimal_places=4) # Up to 999.9999


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
    course_offering = models.ForeignKey(CourseOffering)


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
    course_offering = models.ForeignKey(CourseOffering)


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
    course_offering = models.ForeignKey(CourseOffering)

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
    course_offering = models.ForeignKey(CourseOffering)
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
    course_offering = models.ForeignKey(CourseOffering)
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
    course_offering = models.ForeignKey(CourseOffering)


# CREATE TABLE `summary_posts` (
#   `id` int(11) NOT NULL,
#   `date_id` varchar(11) NOT NULL,
#   `course_id` int(11) NOT NULL,
#   `forum_id` int(11) NOT NULL,
#   `discussion_id` int(11) NOT NULL,
#   `user_id` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
class SummaryPost(models.Model):
    page = models.ForeignKey('Page')
    lms_user = models.ForeignKey(LMSUser)
    posted_at = models.DateTimeField()

    class Meta:
        unique_together = (('lms_user', 'page', 'posted_at'),)


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
    course_offering = models.ForeignKey(CourseOffering)


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
    course_offering = models.ForeignKey(CourseOffering)


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
    course_offering = models.ForeignKey(CourseOffering)

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
    course_offering = models.ForeignKey(CourseOffering)
