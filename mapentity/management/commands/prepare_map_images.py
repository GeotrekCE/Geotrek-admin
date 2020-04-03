from importlib import import_module
import logging

from django.conf import settings
from django.core.management.base import NoArgsCommand

from mapentity.registry import registry

from optparse import make_option


logger = logging.getLogger(__name__)


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--url', '-u', action='store', dest='url',
                    default='http://localhost',
                    help='Base url'),
    )
    help = "Generates all maps images for every objects"

    start_model_msg = "Generate map images for model %s"
    DEFAULT_URL = 'http://localhost'

    def get_models(self):
        # Make sure apps are registered at this point
        import_module(settings.ROOT_URLCONF)
        # For all models registered
        return registry.registry.keys()

    def get_instances(self, model):
        return model.objects.all()

    def handle_noargs(self, **options):
        self.options = options
        for model in self.get_models():
            logger.info(self.start_model_msg % model)
            for instance in self.get_instances(model):
                self.handle_instance(instance)
        logger.info("Done.")

    def handle_instance(self, instance):
        rooturl = self.options.get('url', self.DEFAULT_URL)
        refreshed = instance.prepare_map_image(rooturl)
        if not refreshed:
            logger.info('%s image up-to-date.' % instance.get_map_image_path())
