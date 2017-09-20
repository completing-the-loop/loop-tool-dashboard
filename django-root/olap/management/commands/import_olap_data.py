import sys
import traceback

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from dashboard.models import CourseOffering

from olap.lms_import import ImportLmsData

class Command(BaseCommand):
    help = "Import LMS data for one or more course offerings"

    def add_arguments(self, parser):
        parser.add_argument('offering_code', nargs='*', type=str)

        parser.add_argument('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Attempt to import data for all defined course offerings.',
        )

        parser.add_argument('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clear data from db instead of importing it into db.',
        )

        parser.add_argument('--trace',
            action='store_true',
            dest='trace',
            default=False,
            help='Show a diagnostic trace on error.',
        )

    def handle(self, *args, **options):
        course_codes = options['offering_code']
        verb = 'clear' if options['clear'] else 'import'

        if options['all']:
            if len(course_codes) > 0:
                raise CommandError('Course offering codes cannot be specified at the same time as --all.')
            if len(CourseOffering.objects.all()) == 0:
                raise CommandError('Cannot {} because there are no course offerings in the database.'.format(verb))
            course_offerings = CourseOffering.objects.all()
        else:
            if len(course_codes) == 0:
                raise CommandError('Please supply the code of the course offering to {}.'.format(verb))
            error_msgs = []
            course_offerings = []
            for course_code in course_codes:
                try:
                    course_offerings.append(CourseOffering.objects.get(code=course_code))
                except CourseOffering.DoesNotExist:
                    error_msgs.append('There is no course offering with a code of "{}".'.format(course_code))

            if error_msgs:
                for error_msg in error_msgs:
                    self.stderr.write(error_msg)
                raise CommandError('{} not done.'.format(verb.capitalize()))

        # Do the importing.  Create a separate instance of the importer for each offering, to ensure there's
        # no state kept across offerings.
        error_count = 0
        for course_offering in course_offerings:
            try:
                importer = ImportLmsData(course_offering, just_clear=options['clear'])
                importer.process()
            except:
                error_count += 1
                self.stderr.write('An error occurred when {}ing the data for {}:'.format(verb, course_offering.code))
                if not options['trace']:
                    self.stdout.write('Run again with --trace to show a diagnostic trace.')
                else:
                    exc_info = sys.exc_info()
                    traceback.print_exception(*exc_info)

        plural_offerings = len(course_offerings) != 1
        plural_errors = error_count != 1
        if error_count == 0:
            if plural_offerings:
                self.stdout.write('All {} {}s were successful.'.format(len(course_offerings), verb))
            else:
                self.stdout.write('The {} was successful.'.format(verb))
        else:
            self.stderr.write('{} {}{} out of {} {} unsuccessful.'.format(error_count, verb, 's' if plural_errors else '', len(course_offerings), 'were' if plural_errors else 'was'))
