from contextlib import nullcontext, redirect_stdout
from io import StringIO

from django.apps import apps
from django.core.management import call_command
from django.core.management.commands.migrate import Command as BaseCommand
from django.db import connection

from geotrek.common.utils.postgresql import (
    load_sql_files,
    move_models_to_schemas,
    set_search_path,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        set_search_path()
        for app in apps.get_app_configs():
            move_models_to_schemas(app)
            load_sql_files(app, "pre")
        connection.register_geometry_adapters(connection.connection, True)
        super().handle(*args, **options)
        ctx = redirect_stdout(StringIO()) if options["verbosity"] < 1 else nullcontext()
        with ctx:
            call_command(
                "geotrek_sync_translation_fields",
                "--noinput",
                verbosity=options["verbosity"],
            )
            call_command(
                "update_translation_fields",
                verbosity=options["verbosity"],
            )
        for app in apps.get_app_configs():
            move_models_to_schemas(app)
            load_sql_files(app, "post")
