from django.core.management.base import BaseCommand
from geotrek.feedback.parsers import SuricateParser


class Command(BaseCommand):
    leave_locale_alone = True

    def add_arguments(self, parser):
        # parser.add_argument('-l', dest='limit', type=int, help='Limit number of lines to import')
        # todo
        parser.add_argument(
            "--activities_only",
            dest="activities_only",
            help="Import activities but no statuses nor alerts",
            default=False,
        )
        parser.add_argument(
            "--statuses_only",
            dest="statuses_only",
            help="Import statuses but no activities nor alerts",
            default=False,
        )
        # todo documents

    def handle(self, *args, **options):
        parser = SuricateParser()
        if options["activities_only"] and options["statuses_only"]:
            parser.get_statuses()
            parser.get_activities()
        elif options["statuses_only"]:
            parser.get_statuses()
        elif options["activities_only"]:
            parser.get_activities()
        else:
            parser.initialize_internal_statuses()
            parser.get_statuses()
            parser.get_activities()
            parser.get_alerts()
