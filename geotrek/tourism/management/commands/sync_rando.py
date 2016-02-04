from optparse import make_option
import os
from zipfile import ZipFile

from django.conf import settings
from django.utils import translation, timezone

from geotrek.tourism import models as tourism_models
from geotrek.tourism import views as tourism_views
from geotrek.trekking.management.commands.sync_rando import Command as BaseCommand

# Register mapentity models
from geotrek.tourism import urls  # NOQA


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--with-touristicevents',
                    '-w',
                    action='store_true',
                    dest='with_events',
                    default=False,
                    help='include touristic events by trek in global.zip'),
        make_option('--with-touristiccontent-categories',
                    '-c',
                    action='store',
                    dest='content_categories',
                    default=None,
                    help='include touristic contents by trek in global.zip (filtered by category ID ex: --with-touristiccontent-categories="1,2,3")'),
    )

    def handle(self, *args, **options):
        self.with_events = options.get('with_events', False)
        self.categories = None

        if options.get('content_categories', u""):
            self.categories = options.get('content_categories', u"").split(',')

        super(Command, self).handle(*args, **options)

    def sync_content(self, lang, content):
        if self.skip_pdf:
            return
        view = tourism_views.TouristicContentDocumentPublic.as_view(model=type(content))
        self.sync_object_view(lang, content, view, '{obj.slug}.pdf')

        for picture, resized in content.resized_pictures:
            self.sync_media_file(lang, resized)

    def sync_event(self, lang, event):
        if self.skip_pdf:
            return
        view = tourism_views.TouristicEventDocumentPublic.as_view(model=type(event))
        self.sync_object_view(lang, event, view, '{obj.slug}.pdf')

        for picture, resized in event.resized_pictures:
            self.sync_media_file(lang, resized)

    def sync_tourism(self, lang):
        self.sync_geojson(lang, tourism_views.TouristicContentViewSet, 'touristiccontents.geojson')
        self.sync_geojson(lang, tourism_views.TouristicEventViewSet, 'touristicevents.geojson',
                          params={'ends_after': timezone.now().strftime('%Y-%m-%d')})

        # reopen global zip (closed after trekking sync)
        self.zipfile = ZipFile(os.path.join(self.tmp_root, 'zip', 'treks',
                                            lang, 'global.zip'),
                               'a')

        # picto touristic events
        self.sync_file(lang,
                       os.path.join('tourism', 'touristicevent.svg'),
                       settings.STATIC_ROOT,
                       settings.STATIC_URL,
                       zipfile=self.zipfile)

        # json with
        params = {}

        if self.categories:
            params.update({'categories': ','.join(category for category in self.categories), })

        if self.with_events:
            params.update({'events': '1'})

        self.sync_json(lang, tourism_views.TouristicCategoryView,
                       'touristiccategories',
                       zipfile=self.zipfile, params=params)

        # pictos touristic content catgories
        for category in tourism_models.TouristicContentCategory.objects.all():
            self.sync_media_file(lang, category.pictogram, zipfile=self.zipfile)

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

        # Information desks
        self.sync_geojson(lang, tourism_views.InformationDeskViewSet, 'information_desks.geojson')
        for pk in tourism_models.InformationDeskType.objects.values_list('pk', flat=True):
            name = 'information_desks-{}.geojson'.format(pk)
            self.sync_geojson(lang, tourism_views.InformationDeskViewSet, name, type=pk)
        for desk in tourism_models.InformationDesk.objects.all():
            self.sync_media_file(lang, desk.thumbnail)

        self.zipfile.close()

    def sync_trek_touristiccontents(self, lang, trek, zipfile=None):
        params = {'format': 'geojson',
                  'categories': ','.join(category for category in self.categories), }

        view = tourism_views.TrekTouristicContentViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'touristiccontents.geojson')
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

        for content in trek.touristic_contents.all():
            self.sync_touristiccontent_media(lang, content, zipfile=self.trek_zipfile)

    def sync_trek_touristicevents(self, lang, trek, zipfile=None):
        params = {'format': 'geojson', }
        view = tourism_views.TrekTouristicEventViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'touristicevents.geojson')
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

        for event in trek.touristic_events.all():
            self.sync_touristicevent_media(lang, event, zipfile=self.trek_zipfile)

    def sync_touristicevent_media(self, lang, event, zipfile=None):
        if event.resized_pictures:
            self.sync_media_file(lang, event.resized_pictures[0][1], zipfile=zipfile)
        for picture, resized in event.resized_pictures[1:]:
            self.sync_media_file(lang, resized)

    def sync_touristiccontent_media(self, lang, content, zipfile=None):
        if content.resized_pictures:
            self.sync_media_file(lang, content.resized_pictures[0][1], zipfile=zipfile)
        for picture, resized in content.resized_pictures[1:]:
            self.sync_media_file(lang, resized)

    def sync(self):
        super(Command, self).sync()

        self.sync_static_file('**', 'tourism/touristicevent.svg')
        self.sync_pictograms('**', tourism_models.InformationDeskType)
        self.sync_pictograms('**', tourism_models.TouristicContentCategory)
        self.sync_pictograms('**', tourism_models.TouristicContentType)
        self.sync_pictograms('**', tourism_models.TouristicEventType)

        for lang in self.languages:
            translation.activate(lang)
            self.sync_tourism(lang)

    def sync_trek(self, lang, trek):
        super(Command, self).sync_trek(lang, trek)

        self.trek_zipfile = ZipFile(os.path.join(self.tmp_root, 'zip', 'treks',
                                                 lang, '{pk}.zip'.format(pk=trek.pk)),
                                    'a')

        if self.with_events:
            self.sync_trek_touristicevents(lang, trek, zipfile=self.zipfile)

        if self.categories:
            self.sync_trek_touristiccontents(lang, trek, zipfile=self.zipfile)

        self.trek_zipfile.close()
