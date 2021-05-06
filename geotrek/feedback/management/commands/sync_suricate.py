from django.core.management.base import BaseCommand

from geotrek.feedback.parsers import SuricateParser


class Command(BaseCommand):
    leave_locale_alone = True

    def add_arguments(self, parser):
        # parser.add_argument('-l', dest='limit', type=int, help='Limit number of lines to import')
        # todo
        parser.add_argument(
            "--activities", dest="activities", help="Import activities", default=True
        )
        parser.add_argument(
            "--statuses", dest="statuses", help="Import statuses", default=True
        )

    def handle(self, *args, **options):
        parser = SuricateParser()
        if options["statuses"]:
            parser.get_statuses()
        if options["activities"]:
            parser.get_activities()
