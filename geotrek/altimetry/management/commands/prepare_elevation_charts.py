import logging

from django.conf import settings
from django.core.urlresolvers import NoReverseMatch

from geotrek.common.management.commands.prepare_map_images import Command as PrepareImageCommand

from geotrek.altimetry.models import AltimetryMixin


logger = logging.getLogger(__name__)


class Command(PrepareImageCommand):
    help = "Generates all altimetric profiles"

    start_model_msg = "Generate all elevation charts model %s"

    def get_models(self):
        with_profiles = []
        models = super(Command, self).get_models()
        for model in models:
            if not issubclass(model, AltimetryMixin):
                continue

            try:
                instance = model.objects.all()[0]
                instance.get_elevation_chart_url()
                with_profiles.append(model)
            except (NoReverseMatch, IndexError):
                pass
        return with_profiles

    def handle_instance(self, instance):
        rooturl = self.options.get('url', self.DEFAULT_URL)
        for language, name in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            refreshed = instance.prepare_elevation_chart(language, rooturl)
            if not refreshed:
                logger.info('%s profile up-to-date.' % instance.get_elevation_chart_path(language))
