import importlib
from os.path import join

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from geotrek.common.parsers import ImportError


class Command(BaseCommand):
    leave_locale_alone = True

    def add_arguments(self, parser):
        parser.add_argument(
            "parser",
            help="Parser class name in var/conf/parsers.py (or dotted syntax in python path)",
        )
        parser.add_argument(
            "filename", nargs="?", help="Optional file used to feed database"
        )
        parser.add_argument(
            "-l", dest="limit", type=int, help="Limit number of lines to import"
        )
        parser.add_argument("--encoding", "-e", default="utf8")

    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        limit = options["limit"]
        encoding = options["encoding"]

        if "." in options["parser"]:
            # Python import syntax
            module_name, class_name = options["parser"].rsplit(".", 1)
            module_path = module_name.replace(".", "/") + ".py"
        else:
            # just a class name
            module_path = join(settings.VAR_DIR, "conf/parsers.py")
            module_name = "parsers"
            class_name = options["parser"]

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except FileNotFoundError:
            msg = f"Failed to import parser file '{module_path}'"
            raise CommandError(msg)
        try:
            Parser = getattr(module, class_name)
        except AttributeError:
            msg = f"Failed to import parser class '{class_name}'"
            raise CommandError(msg)
        if not Parser.filename and not Parser.url and not options["filename"]:
            msg = "File path missing"
            raise CommandError(msg)

        def progress_cb(progress, line, eid):
            if verbosity >= 2:
                self.stdout.write(
                    "{line:04d}: {eid: <10} ({progress:02d}%)".format(
                        line=line, eid=eid or "", progress=int(100 * progress)
                    )
                )

        parser = Parser(progress_cb=progress_cb, encoding=encoding)

        try:
            parser.parse(options["filename"], limit=limit)
        except ImportError as e:
            raise CommandError(e)

        if (verbosity >= 1 and parser.warnings) or verbosity >= 2:
            self.stdout.write(parser.report())
