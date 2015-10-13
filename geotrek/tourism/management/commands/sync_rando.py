from optparse import make_option
import os
from zipfile import ZipFile

from django.conf import settings
from django.utils import translation

from geotrek.tourism import (models as tourism_models,
                             views as tourism_views)
from geotrek.tourism.views import TouristicEventViewSet, TouristicContentViewSet
from geotrek.trekking.management.commands.sync_rando import Command as BaseCommand


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--with-events',
                    '-w',
                    action='store_true',
                    dest='with-events',
                    default=False,
                    help='include touristic events'),
        make_option('--content-categories',
                    '-c',
                    action='store',
                    dest='content-categories',
                    default=None,
                    help='include touristic categories separated by commas'),
    )

    def handle(self, *args, **options):
        self.with_events = options.get('with-events', False)
        self.categories = None

        if options.get('content-categories', u""):
            self.categories = options.get('content-categories', u"").split(',')

        super(Command, self).handle(*args, **options)

    def sync_trekking(self, lang):
        super(Command, self).sync_trekking(lang)

        # after base sync_trekking, reopen zip to add features
        zipname = os.path.join('zip', 'treks', lang, 'global.zip')
        zipfullname = os.path.join(self.tmp_root, zipname)
        self.zipfile = ZipFile(zipfullname, 'a')

        # adding custom sync_trek for tourism events
        if self.with_events:
            self.sync_geojson(lang, TouristicEventViewSet, 'touristicevents', zipfile=self.zipfile)

        events = tourism_models.TouristicEvent.objects.existing().order_by('pk')
        events = events.filter(**{'published_{lang}'.format(lang=lang): True})

        if self.source:
            events = events.filter(source__name__in=self.source)

        for event in events:
            self.sync_event(lang, event, zipfile=self.zipfile)

        # adding custom sync_trek for tourism content by categories
        if self.categories:
            name = os.path.join('api', lang, '{name}.geojson'.format(name='touristiccontents'))
            params = {'format': 'geojson',
                      'categories': ','.join(category for category in self.categories)}

            if self.source:
                params['source'] = ','.join(self.source)

            self.sync_view(lang, TouristicContentViewSet.as_view({'get': 'list'}),
                           name, url="/", params=params, zipfile=self.zipfile)

        self.close_zip(self.zipfile, zipname)

    def sync_content(self, lang, content, zipfile=None):
        self.sync_pdf(lang, content, zipfile=zipfile)

        for picture, resized in content.resized_pictures:
            self.sync_media_file(lang, resized, zipfile=zipfile)

    def sync_event(self, lang, event, zipfile=None):
        self.sync_pdf(lang, event, zipfile=zipfile)

        for picture, resized in event.resized_pictures:
            self.sync_media_file(lang, resized)

    def sync_tourism(self, lang):
        self.sync_geojson(lang, tourism_views.TouristicContentViewSet, 'touristiccontents',)
        self.sync_geojson(lang, tourism_views.TouristicEventViewSet, 'touristicevents',)

        contents = tourism_models.TouristicContent.objects.existing().order_by('pk')
        contents = contents.filter(**{'published_{lang}'.format(lang=lang): True})
        if self.source:
            contents = contents.filter(source__name__in=self.source)
        for content in contents:
            self.sync_content(lang, content)

        events = tourism_models.TouristicEvent.objects.existing().order_by('pk')
        events = events.filter(**{'published_{lang}'.format(lang=lang): True})
        if self.source:
            events = events.filter(source__name__in=self.source)
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
