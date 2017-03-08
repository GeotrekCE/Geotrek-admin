import logging

from django.conf import settings
from django.utils.importlib import import_module
from django.apps import apps
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mapentity import registry
from mapentity.middleware import clear_internal_user_cache
from mapentity.registry import create_mapentity_model_permissions

from geotrek.common.mixins import BasePublishableMixin


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create models permissions"

    def execute(self, *args, **options):
        logger.info("Synchronize django permissions")

        for app_config in apps.get_app_configs():
            create_permissions(app_config, [], int(options.get('verbosity', 1)))

        logger.info("Done.")

        logger.info("Synchronize mapentity permissions")

        # Make sure apps are registered at this point
        import_module(settings.ROOT_URLCONF)

        # Tests reset DB so we have to reset this cache too
        clear_internal_user_cache()

        # For all models registered, add missing bits
        for model in registry.registry.keys():
            create_mapentity_model_permissions(model)

        logger.info("Done.")

        logger.info("Synchronize geotrek permissions")

        for content_type in ContentType.objects.all():
            model = content_type.model_class()
            if model and issubclass(model, BasePublishableMixin):
                Permission.objects.get_or_create(
                    codename='publish_%s' % content_type.model,
                    content_type=content_type,
                    defaults={'name': 'Can publish %s' % content_type.name}
                )

        logger.info("Done.")
