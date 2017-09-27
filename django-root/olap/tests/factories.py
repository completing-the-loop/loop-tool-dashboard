import datetime
import factory
from factory import faker
from factory import fuzzy

from django.utils.timezone import get_current_timezone

from dashboard.tests.factories import CourseOfferingFactory
from olap.models import LMSUser
from olap.models import Page
from olap.models import PageVisit


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

class PageFactory(factory.DjangoModelFactory):
    class Meta:
        model = Page

    class Params:
        CONTENT_TYPE_CHOICES = ("resource/%s" % s for s in
            ('x-bb-document', 'x-bb-youtube-mashup', 'lo-podcast', 'x-bb-image', 'x-bb-announcement')
        )
        TITLE_CHOICES = (
            'Practical Debauchery', 'Finding Part-Time Work', 'Making Eyes at your Classmate',
            'Tolerable Sins', 'Nix Your Hangover Now!',
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
        current_tz = get_current_timezone()
        VISITS_START = datetime.datetime(2016, 2, 26, 8, 0, 10)
        VISITS_END = datetime.datetime(2016, 6, 16, 17, 35, 9)

    # visited_at = factory.fuzzy.FuzzyDateTime(start_dt=Params.VISITS_START, end_dt=Params.VISITS_END)
    visited_at = faker.Faker('date_time_between_dates', datetime_start=Params.VISITS_START, datetime_end=Params.VISITS_END, tzinfo=Params.current_tz)
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
