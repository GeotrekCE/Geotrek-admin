import importlib

from django.core.management.base import BaseCommand, CommandError

from geotrek.common.parsers import ImportError


class Command(BaseCommand):
    leave_locale_alone = True

    def add_arguments(self, parser):
        parser.add_argument('parser')
        parser.add_argument('shapefile', nargs="?")
        parser.add_argument('-l', dest='limit', type=int, help='Limit number of lines to import')
        parser.add_argument('--encoding', '-e', default='utf8')

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        limit = options['limit']
        encoding = options['encoding']

        # Validate arguments

        try:
            module_name, class_name = options['parser'].rsplit('.', 1)
            module = importlib.import_module(module_name)
            Parser = getattr(module, class_name)
        except (ImportError, AttributeError):
            raise CommandError("Failed to import parser class '{0}'".format(options['parser']))
        if not Parser.filename and not Parser.url and not options['shapefile']:
            raise CommandError("File path missing")

        def progress_cb(progress, line, eid):
            if verbosity >= 2:
                self.stdout.write("{line:04d}: {eid: <10} ({progress:02d}%)".format(
                    line=line, eid=eid or '', progress=int(100 * progress)))

        parser = Parser(progress_cb=progress_cb, encoding=encoding)

        try:
            parser.parse(options['shapefile'], limit=limit)
        except ImportError as e:
            raise CommandError(e)

        if verbosity >= 1 or parser.warnings:
            self.stdout.write(parser.report())
