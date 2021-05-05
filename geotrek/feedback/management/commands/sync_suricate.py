from django.core.management.base import BaseCommand
from geotrek.feedback.parsers import SuricateParser


class Command(BaseCommand):
    leave_locale_alone = True

    def add_arguments(self, parser):
        parser.add_argument('-l', dest='limit', type=int, help='Limit number of lines to import')
        # parser.add_argument('--encoding', '-e', default='utf8')

    def handle(self, *args, **options):
        parser = SuricateParser()
        print("parsinf")
        parser.get_activities()
        # parser.get_activities(limit)
