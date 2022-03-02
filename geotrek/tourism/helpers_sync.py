from django.conf import settings
from django.db.models import Q
from django.utils import timezone
import os

from geotrek.tourism import views as tourism_views
from geotrek.tourism import models


class SyncRando:
    def __init__(self, sync):
        self.global_sync = sync

    def sync(self, lang):
        self.global_sync.sync_geojson(lang, tourism_views.TouristicContentViewSet, 'touristiccontents.geojson',
                                      type_view={"get": "rando-v2-geojson"})
        self.global_sync.sync_geojson(lang, tourism_views.TouristicEventViewSet, 'touristicevents.geojson',
                                      params={'ends_after': timezone.now().strftime('%Y-%m-%d')})

        # picto touristic events
        self.global_sync.sync_file(lang,
                                   os.path.join('tourism', 'touristicevent.svg'),
                                   settings.STATIC_ROOT,
                                   settings.STATIC_URL,
                                   zipfile=self.global_sync.zipfile)

        # json with
        params = {}

        if self.global_sync.categories:
            params.update({'categories': ','.join(category for category in self.global_sync.categories), })

        if self.global_sync.with_events:
            params.update({'events': '1'})

        self.global_sync.sync_json(lang, tourism_views.TouristicCategoryView,
                                   'touristiccategories',
                                   zipfile=self.global_sync.zipfile, params=params)

        # pictos touristic content catgories
        for category in models.TouristicContentCategory.objects.all():
            self.global_sync.sync_media_file(lang, category.pictogram, zipfile=self.global_sync.zipfile)

        contents = models.TouristicContent.objects.existing().order_by('pk')
        contents = contents.filter(**{'published_{lang}'.format(lang=lang): True})

        if self.global_sync.source:
            contents = contents.filter(source__name__in=self.global_sync.source)

        if self.global_sync.portal:
            contents = contents.filter(Q(portal__name=self.global_sync.portal) | Q(portal=None))

        for content in contents:
            self.sync_content(lang, content)

        events = models.TouristicEvent.objects.existing().order_by('pk')
        events = events.filter(**{'published_{lang}'.format(lang=lang): True})

        if self.global_sync.source:
            events = events.filter(source__name__in=self.global_sync.source)

        if self.global_sync.portal:
            events = events.filter(Q(portal__name=self.global_sync.portal) | Q(portal=None))

        for event in events:
            self.sync_event(lang, event)

        # Information desks
        self.global_sync.sync_geojson(lang, tourism_views.InformationDeskViewSet, 'information_desks.geojson')
        for pk in models.InformationDeskType.objects.values_list('pk', flat=True):
            name = 'information_desks-{}.geojson'.format(pk)
            self.global_sync.sync_geojson(lang, tourism_views.InformationDeskViewSet, name, type=pk)
        for desk in models.InformationDesk.objects.all():
            self.global_sync.sync_media_file(lang, desk.thumbnail)

    def sync_event(self, lang, event):
        self.global_sync.sync_metas(lang, tourism_views.TouristicEventMeta, event)
        self.global_sync.sync_pdf(lang, event,
                                  tourism_views.TouristicEventDocumentPublic.as_view(model=type(event)))
        for picture, resized in event.resized_pictures:
            self.global_sync.sync_media_file(lang, resized)

    def sync_content(self, lang, content):
        self.global_sync.sync_metas(lang, tourism_views.TouristicContentMeta, content)
        self.global_sync.sync_pdf(lang, content,
                                  tourism_views.TouristicContentDocumentPublic.as_view(model=type(content)))
        for picture, resized in content.resized_pictures:
            self.global_sync.sync_media_file(lang, resized)
