from django.conf import settings
from django.db.models import Q

from modeltranslation.utils import build_localized_fieldname

import os

from geotrek.diving import models
from geotrek.diving import views as diving_views


if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from geotrek.sensitivity import views as sensitivity_views
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import views as tourism_views


class SyncRando:
    def __init__(self, sync):
        self.global_sync = sync

    def sync(self, lang):
        models_picto = [models.Practice, models.Difficulty, models.Level]
        self.global_sync.sync_pictograms(lang, models_picto, zipfile=self.global_sync.zipfile)
        self.global_sync.sync_geojson(lang, diving_views.DiveAPIViewSet, 'dives.geojson')

        dives = models.Dive.objects.existing().order_by('pk')
        dives = dives.filter(**{build_localized_fieldname('published', lang): True})

        if self.global_sync.source:
            dives = dives.filter(source__name__in=self.global_sync.source)

        if self.global_sync.portal:
            dives = dives.filter(Q(portal__name=self.global_sync.portal) | Q(portal=None))

        for dive in dives:
            self.sync_detail(lang, dive)

    def sync_pois(self, lang, dive):
        params = {'format': 'geojson'}
        view = diving_views.DivePOIViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'pois.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, pk=dive.pk)

    def sync_services(self, lang, dive):
        view = diving_views.DiveServiceViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'services.geojson')
        self.global_sync.sync_view(lang, view, name, params={'format': 'geojson'}, pk=dive.pk)

    def sync_detail(self, lang, dive):
        self.global_sync.sync_metas(lang, diving_views.DiveMeta, dive)
        self.global_sync.sync_pdf(lang, dive, diving_views.DiveDocumentPublic.as_view(model=type(dive)))
        if 'geotrek.trekking' in settings.INSTALLED_APPS:
            self.sync_pois(lang, dive)
            self.sync_services(lang, dive)
        for picture, resized in dive.resized_pictures:
            self.global_sync.sync_media_file(lang, resized)
        for poi in dive.published_pois:
            if poi.resized_pictures:
                self.global_sync.sync_media_file(lang, poi.resized_pictures[0][1])
            for picture, resized in poi.resized_pictures[1:]:
                self.global_sync.sync_media_file(lang, resized)
            for other_file in poi.files:
                self.global_sync.sync_media_file(lang, other_file.attachment_file)
        if 'geotrek.tourism' in settings.INSTALLED_APPS:
            if self.global_sync.with_events:
                self.sync_touristicevents(lang, dive)
            if self.global_sync.categories:
                self.sync_touristiccontents(lang, dive)
        if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
            self.sync_sensitiveareas(lang, dive)

    def sync_touristiccontents(self, lang, dive):
        params = {'format': 'geojson',
                  'categories': ','.join(category for category in self.global_sync.categories)}
        self.global_sync.get_params_portal(params)
        view = tourism_views.DiveTouristicContentViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'touristiccontents.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, pk=dive.pk)

        for content in dive.touristic_contents.all():
            self.sync_touristiccontent_media(lang, content)

    def sync_touristicevents(self, lang, dive):
        params = {'format': 'geojson'}
        self.global_sync.get_params_portal(params)
        view = tourism_views.DiveTouristicEventViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'touristicevents.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, pk=dive.pk)

        for event in dive.touristic_events.all():
            self.sync_touristicevent_media(lang, event)

    def sync_sensitiveareas(self, lang, dive):
        params = {'format': 'geojson', 'practices': 'Terrestre'}

        view = sensitivity_views.DiveSensitiveAreaViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'sensitiveareas.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, pk=dive.pk)

    def sync_touristicevent_media(self, lang, event, zipfile=None):
        if event.resized_pictures:
            self.global_sync.sync_media_file(lang, event.resized_pictures[0][1], zipfile=zipfile)
        for picture, resized in event.resized_pictures[1:]:
            self.global_sync.sync_media_file(lang, resized)

    def sync_touristiccontent_media(self, lang, content, zipfile=None):
        if content.resized_pictures:
            self.global_sync.sync_media_file(lang, content.resized_pictures[0][1], zipfile=zipfile)
        for picture, resized in content.resized_pictures[1:]:
            self.global_sync.sync_media_file(lang, resized)
