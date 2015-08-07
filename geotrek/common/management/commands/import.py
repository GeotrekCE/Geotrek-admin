import importlib
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

from geotrek.common.parsers import ImportError


class Command(BaseCommand):
    leave_locale_alone = True
    args = '<parser> <shapefile>'
    option_list = BaseCommand.option_list + (
        make_option('-l', dest='limit', type='int',
                    help='Limit number of lines to import'),
    )

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        verbosity = int(options.get('verbosity', '1'))
        limit = options.get('limit')

        # Validate arguments
        if len(args) < 1:
            raise CommandError("Parser module path missing")

        try:
            module_name, class_name = args[0].rsplit('.', 1)
            module = importlib.import_module(module_name)
            Parser = getattr(module, class_name)
        except:
            raise CommandError("Failed to import parser class '{0}'".format(args[0]))

        if not Parser.filename and not Parser.url and len(args) < 2:
            raise CommandError("File path missing")

        def progress_cb(progress, line, eid):
            if verbosity >= 2:
                self.stdout.write("{line:04d}: {eid: <10} ({progress:02d}%)".format(
                    line=line, eid=eid, progress=int(100 * progress)))

        parser = Parser(progress_cb=progress_cb)

        try:
            parser.parse(args[1] if len(args) >= 2 else None, limit=limit)
        except ImportError as e:
            raise CommandError(e)

        if verbosity >= 1 or parser.warnings:
            self.stdout.write(parser.report())
