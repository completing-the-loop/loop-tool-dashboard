import datetime
import factory
from factory import faker
import random

from authtools.models import User

from dashboard.models import CourseOffering
from dashboard.models import CourseRepeatingEvent


class LecturerFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    is_staff = False
    is_superuser = False

    name = factory.Sequence(lambda n: 'Lecturer %d' % n)
    email = factory.Sequence(lambda n: 'lecturer_%d@test.com' % n)
    password = factory.PostGenerationMethodCall('set_password', 'password')

    @classmethod
    def _setup_next_sequence(cls):
        return 1


class CourseOfferingFactory(factory.DjangoModelFactory):
    class Meta:
        model = CourseOffering

    lms_type = CourseOffering.LMS_TYPE_BLACKBOARD
    code = factory.Sequence(lambda n: 'C%d' % n)
    title = factory.Sequence(lambda n: 'CourseOffering %d' % n)
    offering = 'Sem X'
    start_date = faker.Faker('date_object')
    no_weeks = 14

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of owners were passed in so add them
            for owner in extracted:
                self.owners.add(owner)

    @classmethod
    def _setup_next_sequence(cls):
        return 101


class CourseRepeatingEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = CourseRepeatingEvent

    title = factory.Sequence(lambda n: 'CourseRepeatingEvent %d' % n)
    course_offering = factory.SubFactory(CourseOfferingFactory)
    start_week = factory.LazyAttribute(lambda obj: random.randint(1, obj.course_offering.no_weeks)) # This .fuzz() stuff is thanks to levi
    end_week = factory.LazyAttribute(lambda obj: random.randint(obj.start_week, obj.course_offering.no_weeks))
    day_of_week = factory.LazyAttribute(lambda obj: random.randint(0, 6))
    created_at = factory.LazyFunction(datetime.datetime.now)

    @classmethod
    def _setup_next_sequence(cls):
        return 101
