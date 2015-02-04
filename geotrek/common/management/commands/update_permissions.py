from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.auth.management import create_permissions
from django.core.management.base import BaseCommand

from mapentity import registry, logger
from mapentity.registry import create_mapentity_model_permissions

from geotrek.flatpages import models as flatpages_models


class Command(BaseCommand):
    help = "Create models permissions"

    def execute(self, *args, **options):
        logger.info("Synchronize permissions of FlatPage model")

        create_permissions(flatpages_models, None, int(options.get('verbosity', 1)))

        logger.info("Done.")

        logger.info("Synchronize permissions of MapEntity models")

        # Make sure apps are registered at this point
        import_module(settings.ROOT_URLCONF)

        # For all models registered, add missing bits
        for model in registry.registry.keys():
            create_mapentity_model_permissions(model)

        logger.info("Done.")
