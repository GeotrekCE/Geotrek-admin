import os
from zipfile import ZipFile

from django.conf import settings
from django.db.models import Q
from modeltranslation.utils import build_localized_fieldname

from geotrek.common import views as common_views
from geotrek.trekking import models, views

if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import views as tourism_views
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from geotrek.sensitivity import views as sensitivity_views


class SyncRando:
    def __init__(self, sync):
        self.global_sync = sync

    def sync(self, lang):
        self.global_sync.sync_geojson(lang, views.POIAPIViewSet, 'pois.geojson', zipfile=self.global_sync.zipfile)
        self.global_sync.sync_geojson(lang, views.TrekAPIViewSet, 'treks.geojson', zipfile=self.global_sync.zipfile)
        self.global_sync.sync_geojson(lang, views.ServiceAPIViewSet, 'services.geojson',
                                      zipfile=self.global_sync.zipfile)
        self.global_sync.sync_static_file(lang, 'trekking/trek.svg')
        self.global_sync.sync_static_file(lang, 'trekking/itinerancy.svg')
        models_picto = [models.TrekNetwork, models.Practice, models.Accessibility, models.DifficultyLevel,
                        models.POIType, models.ServiceType, models.Route, models.WebLinkCategory]
        self.global_sync.sync_pictograms(lang, models_picto, zipfile=self.global_sync.zipfile)

        treks = models.Trek.objects.existing().order_by('pk')
        treks = treks.filter(
            Q(**{build_localized_fieldname('published', lang): True})
            | Q(**{'trek_parents__parent__{published_lang}'.format(published_lang=build_localized_fieldname('published', lang)): True,
                   'trek_parents__parent__deleted': False})
        )
        if self.global_sync.source:
            treks = treks.filter(source__name__in=self.global_sync.source)

        if self.global_sync.portal:
            treks = treks.filter(Q(portal__name=self.global_sync.portal) | Q(portal=None))

        for trek in treks:
            self.sync_detail(lang, trek)

    def sync_detail(self, lang, trek):
        zipname = os.path.join('zip', 'treks', lang, '{pk}.zip'.format(pk=trek.pk))
        zipfullname = os.path.join(self.global_sync.tmp_root, zipname)
        self.global_sync.mkdirs(zipfullname)
        self.trek_zipfile = ZipFile(zipfullname, 'w')

        self.global_sync.sync_json(lang, common_views.ParametersView, 'parameters', zipfile=self.global_sync.zipfile)
        self.global_sync.sync_json(lang, common_views.ThemeViewSet, 'themes', as_view_args=[{'get': 'list'}],
                                   zipfile=self.global_sync.zipfile)
        self.sync_trek_pois(lang, trek, zipfile=self.global_sync.zipfile)
        if self.global_sync.with_infrastructures:
            self.sync_trek_infrastructures(lang, trek)
        if self.global_sync.with_signages:
            self.sync_trek_signages(lang, trek)
        self.sync_trek_services(lang, trek, zipfile=self.global_sync.zipfile)
        self.sync_trek_gpx(lang, trek)
        self.sync_trek_kml(lang, trek)
        self.global_sync.sync_metas(lang, views.TrekMeta, trek)
        self.global_sync.sync_metas(lang, common_views.Meta)
        if settings.USE_BOOKLET_PDF:
            self.global_sync.sync_pdf(lang, trek, views.TrekDocumentBookletPublic.as_view(model=type(trek)))
        else:
            self.global_sync.sync_pdf(lang, trek, views.TrekDocumentPublic.as_view(model=type(trek)))
        self.global_sync.sync_profile_json(lang, trek)
        if not self.global_sync.skip_profile_png:
            self.global_sync.sync_profile_png(lang, trek, zipfile=self.global_sync.zipfile)
        self.global_sync.sync_dem(lang, trek)
        for desk in trek.information_desks.all():
            self.global_sync.sync_media_file(lang, desk.thumbnail, zipfile=self.trek_zipfile)
        for poi in trek.published_pois:
            self.sync_poi_media(lang, poi)
        self.global_sync.sync_media_file(lang, trek.thumbnail, zipfile=self.global_sync.zipfile)
        for picture, resized in trek.resized_pictures:
            self.global_sync.sync_media_file(lang, resized, zipfile=self.trek_zipfile)

        if self.global_sync.with_events:
            self.sync_trek_touristicevents(lang, trek, zipfile=self.global_sync.zipfile)

        if self.global_sync.categories:
            self.sync_trek_touristiccontents(lang, trek, zipfile=self.global_sync.zipfile)

        if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
            self.sync_trek_sensitiveareas(lang, trek)

        if self.global_sync.verbosity == 2:
            self.global_sync.stdout.write("{lang} {name} ...".format(lang=lang, name=zipname),
                                          ending="")

        self.global_sync.close_zip(self.trek_zipfile, zipname)

    def sync_trek_sensitiveareas(self, lang, trek):
        params = {'format': 'geojson', 'practices': 'Terrestre'}

        view = sensitivity_views.TrekSensitiveAreaViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'sensitiveareas.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, pk=trek.pk)

    def sync_trek_touristiccontents(self, lang, trek, zipfile=None):
        params = {'format': 'geojson',
                  'categories': ','.join(category for category in self.global_sync.categories)}
        self.global_sync.get_params_portal(params)
        view = tourism_views.TrekTouristicContentViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'touristiccontents.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

        for content in trek.touristic_contents.all():
            self.sync_touristiccontent_media(lang, content, zipfile=self.trek_zipfile)

    def sync_trek_touristicevents(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        self.global_sync.get_params_portal(params)
        view = tourism_views.TrekTouristicEventViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'touristicevents.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

        for event in trek.touristic_events.all():
            self.sync_touristicevent_media(lang, event, zipfile=self.trek_zipfile)

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

    def sync_poi_media(self, lang, poi):
        if poi.resized_pictures:
            self.global_sync.sync_media_file(lang, poi.resized_pictures[0][1], zipfile=self.trek_zipfile)
        for picture, resized in poi.resized_pictures[1:]:
            self.global_sync.sync_media_file(lang, resized)
        for other_file in poi.files:
            self.global_sync.sync_media_file(lang, other_file.attachment_file)

    def sync_trek_infrastructures(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        view = views.TrekInfrastructureViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'infrastructures.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

    def sync_trek_signages(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        view = views.TrekSignageViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'signages.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

    def sync_trek_pois(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        view = views.TrekPOIViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'pois.geojson')
        self.global_sync.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

    def sync_trek_services(self, lang, trek, zipfile=None):
        view = views.TrekServiceViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'services.geojson')
        self.global_sync.sync_view(lang, view, name, params={'format': 'geojson'}, zipfile=zipfile, pk=trek.pk)

    def sync_trek_gpx(self, lang, obj):
        self.global_sync.sync_object_view(lang, obj, views.TrekGPXDetail.as_view(), '{obj.slug}.gpx')

    def sync_trek_kml(self, lang, obj):
        self.global_sync.sync_object_view(lang, obj, views.TrekKMLDetail.as_view(), '{obj.slug}.kml')
