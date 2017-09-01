import factory
from authtools.models import User
from factory import faker

from dashboard.models import Course


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


class CourseFactory(factory.DjangoModelFactory):
    class Meta:
        model = Course

    lms_type = Course.LMS_TYPE_BLACKBOARD
    code = factory.Sequence(lambda n: 'C%d' % n)
    title = factory.Sequence(lambda n: 'Course %d' % n)
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

