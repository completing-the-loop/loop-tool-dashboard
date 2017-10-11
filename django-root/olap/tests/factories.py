import datetime
import factory
from factory import faker
from factory import fuzzy

from django.utils.timezone import get_current_timezone

from dashboard.tests.factories import CourseOfferingFactory
from olap.models import LMSUser
from olap.models import Page
from olap.models import PageVisit
from olap.models import SummaryPost


class LMSUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = LMSUser

    lms_user_id = factory.Sequence(lambda n: "%d" % n)
    username = factory.Sequence(lambda n: "u%d" % n)
    course_offering = factory.SubFactory(CourseOfferingFactory)
    firstname = faker.Faker('first_name')
    lastname = faker.Faker('last_name')
    role = 'STUDENT' # Might also be '', associated with staff members.
    email = faker.Faker('email')

    @classmethod
    def _setup_next_sequence(cls):
        return 1000000


PAGE_CONTENT_TYPE_CHOICES = tuple("resource/%s" % s for s in (
    'x-bb-document',
    'x-bb-youtube-mashup',
    'lo-podcast',
    'x-bb-image',
    'x-bb-announcement',
))

class PageFactory(factory.DjangoModelFactory):
    class Meta:
        model = Page

    class Params:
        CONTENT_TYPE_CHOICES = PAGE_CONTENT_TYPE_CHOICES
        TITLE_CHOICES = (
            'Practical Debauchery',
            'Finding Part-Time Work',
            'Making Eyes at your Classmate',
            'Tolerable Sins',
            'Forty Great Hangover Cures',
            'Housemates from Hell Volume IV',
        )

    course_offering = factory.SubFactory(CourseOfferingFactory)
    content_type = fuzzy.FuzzyChoice(choices=Params.CONTENT_TYPE_CHOICES)
    content_id = factory.Sequence(lambda n: n)
    parent_id = 0
    order_no = 0
    title = fuzzy.FuzzyChoice(choices=Params.TITLE_CHOICES)

    @classmethod
    def _setup_next_sequence(cls):
        return 1000000

class PageVisitFactory(factory.DjangoModelFactory):
    class Meta:
        model = PageVisit

    class Params:
        our_tz = get_current_timezone()
        VISITS_START = datetime.datetime(2016, 2, 26, 8, 0, 10, tzinfo=our_tz)
        VISITS_END = datetime.datetime(2016, 6, 16, 17, 35, 9, tzinfo=our_tz)

    visited_at = faker.Faker('date_time_between_dates', datetime_start=Params.VISITS_START, datetime_end=Params.VISITS_END)
    lms_user = factory.SubFactory(LMSUserFactory)
    page = factory.SubFactory(PageFactory)
    # TODO: There's several fields here which are candidates for removal/alteration.  Audit.
    # module = factory.CharField(blank=True, max_length=255) # Is this always a resource/x-bb-* content type?
    action = 'CONTENT_ACCESS' # Also extent: COURSE_ACCESS
    # url = factory.TextField(blank=True)
    # section_id = factory.IntegerField(blank=True, null=True)
    # section_pk = factory.CharField(blank=True, max_length=255)
    # section_order = factory.IntegerField(blank=True, null=True)
    # info = factory.TextField()
    session = None


class SummaryPostFactory(factory.DjangoModelFactory):
    class Meta:
        model = SummaryPost

    class Params:
        our_tz = get_current_timezone()
        VISITS_START = datetime.datetime(2016, 2, 26, 8, 0, 10, tzinfo=our_tz)
        VISITS_END = datetime.datetime(2016, 6, 16, 17, 35, 9, tzinfo=our_tz)

    page = factory.SubFactory(PageFactory)
    lms_user = factory.SubFactory(LMSUserFactory)
    posted_at = faker.Faker('date_time_between_dates', datetime_start=Params.VISITS_START, datetime_end=Params.VISITS_END)

"""
# TODO: Save these for another day.
class LMSSessionFactory(factory.DjangoModelFactory):
    class Meta:
        model = LMSSession


class SubmissionAttemptFactory(factory.DjangoModelFactory):
    class Meta:
        model = SubmissionAttempt


class SubmissionTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = SubmissionType
"""
