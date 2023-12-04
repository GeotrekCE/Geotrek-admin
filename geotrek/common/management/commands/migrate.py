from django.apps import apps
from django.core.management import call_command
from django.core.management.commands.migrate import Command as BaseCommand

from geotrek.common.utils.postgresql import move_models_to_schemas, load_sql_files, set_search_path


class Command(BaseCommand):
    def handle(self, *args, **options):
        set_search_path()
        for app in apps.get_app_configs():
            move_models_to_schemas(app)
            load_sql_files(app, 'pre')
        super().handle(*args, **options)
        call_command('sync_translation_fields', '--noinput')
        call_command('update_translation_fields')
        for app in apps.get_app_configs():
            move_models_to_schemas(app)
            load_sql_files(app, 'post')
