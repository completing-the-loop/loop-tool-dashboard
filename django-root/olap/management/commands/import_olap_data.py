from django.core.management.base import BaseCommand, CommandError

from dashboard.models import CourseOffering

from ...lms_import import ImportLmsData

class Command(BaseCommand):
    help = "Import LMS data for one or more course offerings"

    def add_arguments(self, parser):
        parser.add_argument('offering_code', nargs='+', type=str)

        parser.add_argument('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clear data from db instead of importing it into db',
        )

    def handle(self, *args, **options):
        course_codes = options['offering_code']
        verb = 'clear' if options['clear'] else 'import'

        if course_codes == ['all']:
            if len(CourseOffering.objects.all()) == 0:
                raise CommandError('Cannot {} because there are no course offerings in the database.'.format(verb))
            course_codes = tuple(course_offering.code for course_offering in CourseOffering.objects.all())
        else:
            co_errors = []
            for course_code in course_codes:
                if not CourseOffering.objects.filter(code=course_code).exists():
                    co_errors.append('There is no course offering with a code of "{}".'.format(course_code))

            if co_errors:
                for co_error in co_errors:
                    self.stderr.write(co_error)
                raise CommandError('{} not done.'.format(verb.capitalize()))

            # Remove possible duplicates (won't preserve cmd-line order)
            course_codes = tuple(set(course_codes))

        # Do the importing.  Create a separate instance of the importer for each offering, to ensure there's
        # no state kept across offerings.
        for course_code in course_codes:
            importer = ImportLmsData(course_code, just_clear=options['clear'])
            importer.process()
