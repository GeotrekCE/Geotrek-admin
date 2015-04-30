from django.conf import settings
from django.utils import translation

from geotrek.tourism import models as tourism_models
from geotrek.tourism.views import TouristicContentViewSet, TouristicEventViewSet
from geotrek.trekking.management.commands.sync_rando import Command as BaseCommand

# Register mapentity models
from geotrek.tourism import urls  # NOQA


class Command(BaseCommand):
    def sync_content(self, lang, content):
        self.sync_pdf(lang, content)

        for picture, resized in content.resized_pictures:
            self.sync_media_file(resized)

    def sync_event(self, lang, event):
        self.sync_pdf(lang, event)

        for picture, resized in event.resized_pictures:
            self.sync_media_file(resized)

    def sync_tourism(self, lang):
        self.sync_geojson(lang, TouristicContentViewSet, 'touristiccontents')
        self.sync_geojson(lang, TouristicEventViewSet, 'touristicevents')

        contents = tourism_models.TouristicContent.objects.existing().order_by('pk')
        contents = contents.filter(**{'published_{lang}'.format(lang=lang): True})
        for content in contents:
            self.sync_content(lang, content)

        events = tourism_models.TouristicEvent.objects.existing().order_by('pk')
        events = events.filter(**{'published_{lang}'.format(lang=lang): True})
        for event in events:
            self.sync_event(lang, event)

    def sync(self):
        super(Command, self).sync()

        self.sync_static_file('**', 'tourism/touristicevent.svg')
        self.sync_pictograms('**', tourism_models.InformationDeskType)
        self.sync_pictograms('**', tourism_models.TouristicContentCategory)
        self.sync_pictograms('**', tourism_models.TouristicContentType)
        self.sync_pictograms('**', tourism_models.TouristicEventType)

        for lang in settings.MODELTRANSLATION_LANGUAGES:
            translation.activate(lang)
            self.sync_tourism(lang)
