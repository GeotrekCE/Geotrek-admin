import importlib

from django.core.management.base import BaseCommand, CommandError

from geotrek.common.parsers import FatalImportError


class Command(BaseCommand):
    leave_locale_alone = True
    args = '<parser> <shapefile>'

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', '1'))

        # Validate arguments
        if len(args) != 2:
            raise CommandError("Parser and/or filename missing")

        try:
            module_name, class_name = args[0].rsplit('.', 1)
            module = importlib.import_module(module_name)
            Parser = getattr(module, class_name)
        except:
            raise CommandError("Failed to import parser class '{0}'".format(args[0]))

        def progress_cb(progress):
            if verbosity >= 2:
                self.stdout.write("{progress:02d}%".format(progress=int(100 * progress)))

        parser = Parser(progress_cb=progress_cb)

        try:
            parser.parse(args[1])
        except FatalImportError as e:
            raise CommandError(e)

        if verbosity >= 1:
            self.stdout.write(parser.report())
