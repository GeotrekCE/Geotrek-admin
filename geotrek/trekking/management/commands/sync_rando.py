import argparse
import logging
import filecmp
import os
import re
import shutil
from time import sleep
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.test.client import RequestFactory
from django.utils import translation, timezone
from django.utils.translation import ugettext as _
from landez import TilesManager
from landez.sources import DownloadError
from geotrek.common.models import FileType  # NOQA
from geotrek.altimetry.views import ElevationProfile, ElevationArea, serve_elevation_chart
from geotrek.common import models as common_models
from geotrek.common.views import ThemeViewSet
from geotrek.core.views import ParametersView
from geotrek.feedback.views import FeedbackOptionsView, CategoryList as FeedbackCategoryList
from geotrek.flatpages.models import FlatPage
from geotrek.flatpages.views import FlatPageViewSet, FlatPageMeta
from geotrek.infrastructure import models as infrastructure_models
from geotrek.infrastructure.views import InfrastructureViewSet
from geotrek.signage.views import SignageViewSet
from geotrek.tourism import models as tourism_models
from geotrek.tourism import views as tourism_views
from geotrek.trekking import models as trekking_models
from geotrek.trekking.views import (TrekViewSet, POIViewSet, TrekPOIViewSet,
                                    TrekGPXDetail, TrekKMLDetail, TrekServiceViewSet,
                                    ServiceViewSet, TrekDocumentPublic, TrekMeta, Meta,
                                    TrekInfrastructureViewSet, TrekSignageViewSet,)
if 'geotrek.diving' in settings.INSTALLED_APPS:
    from geotrek.diving import models as diving_models
    from geotrek.diving import views as diving_views
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from geotrek.sensitivity import models as sensitivity_models
    from geotrek.sensitivity import views as sensitivity_views

# Register mapentity models
from geotrek.trekking import urls  # NOQA
from geotrek.tourism import urls  # NOQA


logger = logging.getLogger(__name__)


class ZipTilesBuilder(object):
    def __init__(self, zipfile, prefix="", **builder_args):
        self.zipfile = zipfile
        self.prefix = prefix
        builder_args['tile_format'] = self.format_from_url(builder_args['tiles_url'])
        self.tm = TilesManager(**builder_args)

        if not isinstance(settings.MOBILE_TILES_URL, str) and len(settings.MOBILE_TILES_URL) > 1:
            for url in settings.MOBILE_TILES_URL[1:]:
                args = builder_args
                args['tiles_url'] = url
                args['tile_format'] = self.format_from_url(args['tiles_url'])
                self.tm.add_layer(TilesManager(**args), opacity=1)

        self.tiles = set()

    def format_from_url(self, url):
        """
        Try to guess the tile mime type from the tiles URL.
        Should work with basic stuff like `http://osm.org/{z}/{x}/{y}.png`
        or funky stuff like WMTS (`http://server/wmts?LAYER=...FORMAT=image/jpeg...)
        """
        m = re.search(r'FORMAT=([a-zA-Z/]+)&', url)
        if m:
            return m.group(1)
        return url.rsplit('.')[-1]

    def add_coverage(self, bbox, zoomlevels):
        self.tiles |= set(self.tm.tileslist(bbox, zoomlevels))

    def run(self):
        for tile in self.tiles:
            name = '{prefix}{0}/{1}/{2}{ext}'.format(
                *tile,
                prefix=self.prefix,
                ext=settings.MOBILE_TILES_EXTENSION or self.tm._tile_extension
            )
            try:
                data = self.tm.tile(tile)
            except DownloadError:
                logger.warning("Failed to download tile %s" % name)
            else:
                self.zipfile.writestr(name, data)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('--url', '-u', dest='url', default='http://localhost', help='Base url')
        parser.add_argument('--rando-url', '-r', dest='rando_url', default='http://localhost',
                            help='Base url of public rando site')
        parser.add_argument('--source', '-s', dest='source', default=None, help='Filter by source(s)')
        parser.add_argument('--portal', '-P', dest='portal', default=None, help='Filter by portal(s)')
        parser.add_argument('--skip-pdf', '-p', action='store_true', dest='skip_pdf', default=False,
                            help='Skip generation of PDF files')
        parser.add_argument('--skip-tiles', '-t', action='store_true', dest='skip_tiles', default=False,
                            help='Skip generation of zip tiles files')
        parser.add_argument('--skip-dem', '-d', action='store_true', dest='skip_dem', default=False,
                            help='Skip generation of DEM files for 3D')
        parser.add_argument('--skip-profile-png', '-e', action='store_true', dest='skip_profile_png', default=False,
                            help='Skip generation of PNG elevation profile'),
        parser.add_argument('--languages', '-l', dest='languages', default='', help='Languages to sync')
        parser.add_argument('--with-touristicevents', '-w', action='store_true', dest='with_events', default=False,
                            help='include touristic events')
        parser.add_argument('--with-touristiccontent-categories', '-c', dest='content_categories',
                            default=None, help='include touristic contents '
                            '(filtered by category ID ex: --with-touristiccontent-categories="1,2,3")'),
        parser.add_argument('--with-signages', '-g', action='store_true', dest='with_signages', default=False,
                            help='include signages')
        parser.add_argument('--with-infrastructures', '-i', action='store_true', dest='with_infrastructures',
                            default=False, help='include infrastructures')
        parser.add_argument('--with-dives', action='store_true', dest='with_dives',
                            default=False, help='include dives')
        parser.add_argument('--task', default=None, help=argparse.SUPPRESS)

    def mkdirs(self, name):
        dirname = os.path.dirname(name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def sync_global_tiles(self):
        """ Creates a tiles file on the global extent.
        """
        zipname = os.path.join('zip', 'tiles', 'global.zip')

        if self.verbosity == 2:
            self.stdout.write("\x1b[36m**\x1b[0m \x1b[1m{name}\x1b[0m ...".format(name=zipname), ending="")
            self.stdout._out.flush()

        global_extent = settings.LEAFLET_CONFIG['SPATIAL_EXTENT']

        logger.info("Global extent is %s" % str(global_extent))
        global_file = os.path.join(self.tmp_root, zipname)

        logger.info("Build global tiles file...")
        self.mkdirs(global_file)

        zipfile = ZipFile(global_file, 'w')
        tiles = ZipTilesBuilder(zipfile, **self.builder_args)
        tiles.add_coverage(bbox=global_extent,
                           zoomlevels=settings.MOBILE_TILES_GLOBAL_ZOOMS)
        tiles.run()
        self.close_zip(zipfile, zipname)

    def sync_trek_tiles(self, trek):
        """ Creates a tiles file for the specified Trek object.
        """
        zipname = os.path.join('zip', 'tiles', '{pk}.zip'.format(pk=trek.pk))

        if self.verbosity == 2:
            self.stdout.write("{name} ...".format(name=zipname), ending="")
            self.stdout._out.flush()

        trek_file = os.path.join(self.tmp_root, zipname)

        def _radius2bbox(lng, lat, radius):
            return (lng - radius, lat - radius,
                    lng + radius, lat + radius)

        self.mkdirs(trek_file)

        zipfile = ZipFile(trek_file, 'w')
        tiles = ZipTilesBuilder(zipfile, **self.builder_args)

        geom = trek.geom
        if geom.geom_type == 'MultiLineString':
            geom = geom[0]  # FIXME
        geom.transform(4326)

        for (lng, lat) in geom.coords:
            large = _radius2bbox(lng, lat, settings.MOBILE_TILES_RADIUS_LARGE)
            small = _radius2bbox(lng, lat, settings.MOBILE_TILES_RADIUS_SMALL)
            tiles.add_coverage(bbox=large, zoomlevels=settings.MOBILE_TILES_LOW_ZOOMS)
            tiles.add_coverage(bbox=small, zoomlevels=settings.MOBILE_TILES_HIGH_ZOOMS)

        tiles.run()
        self.close_zip(zipfile, zipname)

    def sync_view(self, lang, view, name, url='/', params={}, zipfile=None, fix2028=False, **kwargs):
        if self.verbosity == 2:
            self.stdout.write("{lang} {name} ...".format(lang=lang, name=name), ending="")
            self.stdout._out.flush()
        fullname = os.path.join(self.tmp_root, name)
        self.mkdirs(fullname)
        request = self.factory.get(url, params, HTTP_HOST=self.host, secure=self.secure)
        request.LANGUAGE_CODE = lang
        request.user = AnonymousUser()
        try:
            response = view(request, **kwargs)
            if hasattr(response, 'render'):
                response.render()
        except Exception as e:
            self.successfull = False
            if self.verbosity == 2:
                self.stdout.write("\x1b[3D\x1b[31mfailed ({})\x1b[0m".format(e))
            if settings.DEBUG:
                raise
            return
        if response.status_code != 200:
            self.successfull = False
            if self.verbosity > 0:
                self.stderr.write(self.style.ERROR("failed (HTTP {code})".format(code=response.status_code)))
            return
        f = open(fullname, 'wb')
        if isinstance(response, StreamingHttpResponse):
            content = b''.join(response.streaming_content)
        else:
            content = response.content
        # Fix strange unicode characters 2028 and 2029 that make Geotrek-rando crash
        if fix2028:
            content = content.replace(b'\\u2028', b'\\n')
            content = content.replace(b'\\u2029', b'\\n')
        f.write(content)
        f.close()
        oldfilename = os.path.join(self.dst_root, name)
        # If new file is identical to old one, don't recreate it. This will help backup
        if os.path.isfile(oldfilename) and filecmp.cmp(fullname, oldfilename):
            os.unlink(fullname)
            os.link(oldfilename, fullname)
            if self.verbosity == 2:
                self.stdout.write("unchanged")
        else:
            if self.verbosity == 2:
                self.stdout.write("generated")
        # FixMe: Find why there are duplicate files.
        if zipfile:
            if name not in zipfile.namelist():
                zipfile.write(fullname, name)

    def sync_json(self, lang, viewset, name, zipfile=None, params={}, as_view_args=[], **kwargs):
        view = viewset.as_view(*as_view_args)
        name = os.path.join('api', lang, '{name}.json'.format(name=name))
        if self.source:
            params['source'] = ','.join(self.source)
        if self.portal:
            params['portal'] = ','.join(self.portal)
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, fix2028=True, **kwargs)

    def sync_geojson(self, lang, viewset, name, zipfile=None, params={}, **kwargs):
        view = viewset.as_view({'get': 'list'})
        name = os.path.join('api', lang, name)
        params = params.copy()
        params.update({'format': 'geojson'})

        if self.source:
            params['source'] = ','.join(self.source)

        if self.portal:
            params['portal'] = ','.join(self.portal)

        self.sync_view(lang, view, name, params=params, zipfile=zipfile, fix2028=True, **kwargs)

    def sync_trek_infrastructures(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        view = TrekInfrastructureViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'infrastructures.geojson')
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

    def sync_trek_signages(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        view = TrekSignageViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'signages.geojson')
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

    def sync_trek_pois(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        view = TrekPOIViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'pois.geojson')
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

    def sync_trek_services(self, lang, trek, zipfile=None):
        view = TrekServiceViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'services.geojson')
        self.sync_view(lang, view, name, params={'format': 'geojson'}, zipfile=zipfile, pk=trek.pk)

    def sync_dive_pois(self, lang, dive):
        params = {'format': 'geojson'}
        view = diving_views.DivePOIViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'pois.geojson')
        self.sync_view(lang, view, name, params=params, pk=dive.pk)

    def sync_dive_services(self, lang, dive):
        view = diving_views.DiveServiceViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'services.geojson')
        self.sync_view(lang, view, name, params={'format': 'geojson'}, pk=dive.pk)

    def sync_object_view(self, lang, obj, view, basename_fmt, zipfile=None, params={}, **kwargs):
        modelname = obj._meta.model_name
        name = os.path.join('api', lang, '{modelname}s'.format(modelname=modelname), str(obj.pk), basename_fmt.format(obj=obj))
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=obj.pk, **kwargs)

    def sync_profile_json(self, lang, obj, zipfile=None):
        view = ElevationProfile.as_view(model=type(obj))
        self.sync_object_view(lang, obj, view, 'profile.json', zipfile=zipfile)

    def sync_profile_png(self, lang, obj, zipfile=None):
        view = serve_elevation_chart
        model_name = type(obj)._meta.model_name
        self.sync_object_view(lang, obj, view, 'profile.png', zipfile=zipfile, model_name=model_name, from_command=True)

    def sync_dem(self, lang, obj):
        if self.skip_dem:
            return
        view = ElevationArea.as_view(model=type(obj))
        self.sync_object_view(lang, obj, view, 'dem.json')

    def sync_gpx(self, lang, obj):
        self.sync_object_view(lang, obj, TrekGPXDetail.as_view(), '{obj.slug}.gpx')

    def sync_kml(self, lang, obj):
        self.sync_object_view(lang, obj, TrekKMLDetail.as_view(), '{obj.slug}.kml')

    def sync_meta(self, lang):
        name = os.path.join('meta', lang, 'index.html')

        self.sync_view(lang, Meta.as_view(), name, params={'rando_url': self.rando_url, 'lang': lang,
                                                           'portal': '' if not self.portal else self.portal[0]})

    def sync_trek_meta(self, lang, obj):
        name = os.path.join('meta', lang, obj.rando_url, 'index.html')
        self.sync_view(lang, TrekMeta.as_view(), name, pk=obj.pk,
                       params={'rando_url': self.rando_url, 'lang': lang,
                               'portal': '' if not self.portal else self.portal[0]})

    def sync_touristiccontent_meta(self, lang, obj):
        name = os.path.join('meta', lang, obj.rando_url, 'index.html')
        self.sync_view(lang, tourism_views.TouristicContentMeta.as_view(), name, pk=obj.pk,
                       params={'rando_url': self.rando_url})

    def sync_touristicevent_meta(self, lang, obj):
        name = os.path.join('meta', lang, obj.rando_url, 'index.html')
        self.sync_view(lang, tourism_views.TouristicEventMeta.as_view(), name, pk=obj.pk,
                       params={'rando_url': self.rando_url})

    def sync_dive_meta(self, lang, obj):
        name = os.path.join('meta', lang, obj.rando_url, 'index.html')
        self.sync_view(lang, diving_views.DiveMeta.as_view(), name, pk=obj.pk,
                       params={'rando_url': self.rando_url})

    def sync_file(self, lang, name, src_root, url, zipfile=None):
        url = url.strip('/')
        src = os.path.join(src_root, name)
        dst = os.path.join(self.tmp_root, url, name)
        self.mkdirs(dst)
        if not os.path.isfile(src):
            self.successfull = False
            if self.verbosity == 2:
                self.stdout.write("\x1b[36m{lang}\x1b[0m \x1b[1m{url}/{name}\x1b[0m \x1b[31mfile does not exist\x1b[0m".format(lang=lang, url=url, name=name))
            return
        if not os.path.isfile(dst):
            os.link(src, dst)
        if zipfile:
            zipfile.write(dst, os.path.join(url, name))
        if self.verbosity == 2:
            self.stdout.write("{lang} {url}/{name} copied".format(lang=lang, url=url, name=name))

    def sync_static_file(self, lang, name):
        self.sync_file(lang, name, settings.STATIC_ROOT, settings.STATIC_URL)

    def sync_media_file(self, lang, field, zipfile=None):
        if field and field.name:
            self.sync_file(lang, field.name, settings.MEDIA_ROOT, settings.MEDIA_URL, zipfile=zipfile)

    def sync_pictograms(self, lang, model, zipfile=None):
        for obj in model.objects.all():
            self.sync_media_file(lang, obj.pictogram, zipfile=zipfile)

    def sync_poi_media(self, lang, poi):
        if poi.resized_pictures:
            self.sync_media_file(lang, poi.resized_pictures[0][1], zipfile=self.trek_zipfile)
        for picture, resized in poi.resized_pictures[1:]:
            self.sync_media_file(lang, resized)
        for other_file in poi.files:
            self.sync_media_file(lang, other_file.attachment_file)

    def sync_trek(self, lang, trek):
        zipname = os.path.join('zip', 'treks', lang, '{pk}.zip'.format(pk=trek.pk))
        zipfullname = os.path.join(self.tmp_root, zipname)
        self.mkdirs(zipfullname)
        self.trek_zipfile = ZipFile(zipfullname, 'w')

        self.sync_json(lang, ParametersView, 'parameters', zipfile=self.zipfile)
        self.sync_json(lang, ThemeViewSet, 'themes', as_view_args=[{'get': 'list'}], zipfile=self.zipfile)
        self.sync_trek_pois(lang, trek, zipfile=self.zipfile)
        if self.with_infrastructures:
            self.sync_trek_infrastructures(lang, trek)
        if self.with_signages:
            self.sync_trek_signages(lang, trek)
        self.sync_trek_services(lang, trek, zipfile=self.zipfile)
        self.sync_gpx(lang, trek)
        self.sync_kml(lang, trek)
        self.sync_trek_meta(lang, trek)
        self.sync_pdf(lang, trek, TrekDocumentPublic.as_view(model=type(trek)))
        if settings.USE_BOOKLET_PDF:
            modelname = trek._meta.model_name
            name_pdf = os.path.join('api', lang, '{modelname}s'.format(modelname=modelname), str(trek.pk))
            original_pdf = os.path.join(self.tmp_root, name_pdf, '{obj.slug}.pdf'.format(obj=trek))
            self.change_pdf_booklet(original_pdf)

        self.sync_profile_json(lang, trek)
        if not self.skip_profile_png:
            self.sync_profile_png(lang, trek, zipfile=self.zipfile)
        self.sync_dem(lang, trek)
        for desk in trek.information_desks.all():
            self.sync_media_file(lang, desk.thumbnail, zipfile=self.trek_zipfile)
        for poi in trek.published_pois:
            self.sync_poi_media(lang, poi)
        self.sync_media_file(lang, trek.thumbnail, zipfile=self.zipfile)
        for picture, resized in trek.resized_pictures:
            self.sync_media_file(lang, resized, zipfile=self.trek_zipfile)

        if self.with_events:
            self.sync_trek_touristicevents(lang, trek, zipfile=self.zipfile)

        if self.categories:
            self.sync_trek_touristiccontents(lang, trek, zipfile=self.zipfile)

        if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
            self.sync_trek_sensitiveareas(lang, trek)

        if self.verbosity == 2:
            self.stdout.write("{lang} {name} ...".format(lang=lang, name=zipname),
                              ending="")

        self.close_zip(self.trek_zipfile, zipname)

    def close_zip(self, zipfile, name):
        oldzipfilename = os.path.join(self.dst_root, name)
        zipfilename = os.path.join(self.tmp_root, name)
        try:
            oldzipfile = ZipFile(oldzipfilename, 'r')
        except IOError:
            uptodate = False
        else:
            old = set([(zi.filename, zi.CRC) for zi in oldzipfile.infolist()])
            new = set([(zi.filename, zi.CRC) for zi in zipfile.infolist()])
            uptodate = (old == new)
            oldzipfile.close()

        zipfile.close()
        if uptodate:
            stat = os.stat(oldzipfilename)
            os.utime(zipfilename, (stat.st_atime, stat.st_mtime))

        if self.verbosity == 2:
            if uptodate:
                self.stdout.write("unchanged")
            else:
                self.stdout.write("zipped")

    def sync_flatpages(self, lang):
        self.sync_geojson(lang, FlatPageViewSet, 'flatpages.geojson', zipfile=self.zipfile)
        flatpages = FlatPage.objects.filter(published=True)
        if self.source:
            flatpages = flatpages.filter(source__name__in=self.source)
        if self.portal:
            flatpages = flatpages.filter(Q(portal__name__in=self.portal) | Q(portal=None))
        for flatpage in flatpages:
            name = os.path.join('meta', lang, flatpage.rando_url, 'index.html')
            self.sync_view(lang, FlatPageMeta.as_view(), name, pk=flatpage.pk, params={'rando_url': self.rando_url})

    def sync_trekking(self, lang):
        zipname = os.path.join('zip', 'treks', lang, 'global.zip')
        zipfullname = os.path.join(self.tmp_root, zipname)
        self.mkdirs(zipfullname)
        self.zipfile = ZipFile(zipfullname, 'w')

        self.sync_geojson(lang, TrekViewSet, 'treks.geojson', zipfile=self.zipfile)
        self.sync_geojson(lang, POIViewSet, 'pois.geojson')
        if self.with_infrastructures:
            self.sync_geojson(lang, InfrastructureViewSet, 'infrastructures.geojson')
            self.sync_static_file(lang, 'infrastructure/picto-infrastructure.png')
        if self.with_signages:
            self.sync_geojson(lang, SignageViewSet, 'signages.geojson')
            self.sync_static_file(lang, 'signage/picto-signage.png')
        if 'geotrek.flatpages' in settings.INSTALLED_APPS:
            self.sync_flatpages(lang)
        self.sync_geojson(lang, ServiceViewSet, 'services.geojson', zipfile=self.zipfile)
        self.sync_view(lang, FeedbackCategoryList.as_view(),
                       os.path.join('api', lang, 'feedback', 'categories.json'),
                       zipfile=self.zipfile)
        self.sync_view(lang, FeedbackOptionsView.as_view(),
                       os.path.join('api', lang, 'feedback', 'options.json'),
                       zipfile=self.zipfile)
        self.sync_static_file(lang, 'trekking/trek.svg')
        self.sync_static_file(lang, 'trekking/itinerancy.svg')
        self.sync_pictograms(lang, common_models.Theme, zipfile=self.zipfile)
        self.sync_pictograms(lang, common_models.RecordSource, zipfile=self.zipfile)
        if self.with_signages or self.with_infrastructures:
            self.sync_pictograms(lang, infrastructure_models.InfrastructureType)
        self.sync_pictograms(lang, trekking_models.TrekNetwork, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.Practice, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.Accessibility, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.DifficultyLevel, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.POIType, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.ServiceType, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.Route, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.WebLinkCategory)
        if self.with_dives:
            self.sync_pictograms(lang, diving_models.Practice)
            self.sync_pictograms(lang, diving_models.Difficulty)
            self.sync_pictograms(lang, diving_models.Level)

        treks = trekking_models.Trek.objects.existing().order_by('pk')
        treks = treks.filter(
            Q(**{'published_{lang}'.format(lang=lang): True})
            | Q(**{'trek_parents__parent__published_{lang}'.format(lang=lang): True,
                   'trek_parents__parent__deleted': False})
        )

        if self.source:
            treks = treks.filter(source__name__in=self.source)

        if self.portal:
            treks = treks.filter(Q(portal__name__in=self.portal) | Q(portal=None))

        for trek in treks:
            self.sync_trek(lang, trek)

        if self.with_dives:
            self.sync_dives(lang)

        self.sync_tourism(lang)
        self.sync_meta(lang)

        if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
            self.sync_sensitiveareas(lang)

        if self.verbosity == 2:
            self.stdout.write("{lang} {name} ...".format(lang=lang, name=zipname), ending="")

        self.close_zip(self.zipfile, zipname)

    def sync_tiles(self):
        if not self.skip_tiles:

            if self.celery_task:
                self.celery_task.update_state(
                    state='PROGRESS',
                    meta={
                        'name': self.celery_task.name,
                        'current': 10,
                        'total': 100,
                        'infos': "{}".format(_("Global tiles syncing ..."))
                    }
                )

            self.sync_global_tiles()

            if self.celery_task:
                self.celery_task.update_state(
                    state='PROGRESS',
                    meta={
                        'name': self.celery_task.name,
                        'current': 20,
                        'total': 100,
                        'infos': "{}".format(_("Trek tiles syncing ..."))
                    }
                )

            treks = trekking_models.Trek.objects.existing().order_by('pk')
            if self.source:
                treks = treks.filter(source__name__in=self.source)

            if self.portal:
                treks = treks.filter(Q(portal__name__in=self.portal) | Q(portal=None))

            for trek in treks:
                if trek.any_published or any([parent.any_published for parent in trek.parents]):
                    self.sync_trek_tiles(trek)

            if self.celery_task:
                self.celery_task.update_state(
                    state='PROGRESS',
                    meta={
                        'name': self.celery_task.name,
                        'current': 30,
                        'total': 100,
                        'infos': "{}".format(_("Tiles synced ..."))
                    }
                )

    def sync_pdf(self, lang, obj, view):
        if self.skip_pdf:
            return
        try:
            file_type = FileType.objects.get(type="Topoguide")
        except FileType.DoesNotExist:
            file_type = None
        attachments = common_models.Attachment.objects.attachments_for_object_only_type(obj, file_type)
        if attachments:
            path = attachments[0].attachment_file.name
            modelname = obj._meta.model_name
            src = os.path.join(settings.MEDIA_ROOT, path)
            dst = os.path.join(self.tmp_root, 'api', lang, '{modelname}s'.format(modelname=modelname), str(obj.pk), obj.slug + '.pdf')
            self.mkdirs(dst)
            os.link(src, dst)
            if self.verbosity == 2:
                self.stdout.write("\x1b[36m{lang}\x1b[0m \x1b[1m{dst}\x1b[0m \x1b[32mcopied\x1b[0m".format(lang=lang, dst=dst))
        elif settings.ONLY_EXTERNAL_PUBLIC_PDF:
            return
        else:
            params = {}
            if self.source:
                params['source'] = self.source[0]
            if self.portal:
                params['portal'] = self.portal[0]
            self.sync_object_view(lang, obj, view, '{obj.slug}.pdf', params=params, slug=obj.slug)

    def sync_content(self, lang, content):
        self.sync_touristiccontent_meta(lang, content)
        self.sync_pdf(lang, content, tourism_views.TouristicContentDocumentPublic.as_view(model=type(content)))
        for picture, resized in content.resized_pictures:
            self.sync_media_file(lang, resized)

    def sync_event(self, lang, event):
        self.sync_touristicevent_meta(lang, event)
        self.sync_pdf(lang, event, tourism_views.TouristicEventDocumentPublic.as_view(model=type(event)))
        for picture, resized in event.resized_pictures:
            self.sync_media_file(lang, resized)

    def sync_dive(self, lang, dive):
        self.sync_dive_meta(lang, dive)
        self.sync_pdf(lang, dive, diving_views.DiveDocumentPublic.as_view(model=type(dive)))
        self.sync_dive_pois(lang, dive)
        self.sync_dive_services(lang, dive)
        for picture, resized in dive.resized_pictures:
            self.sync_media_file(lang, resized)
        for poi in dive.published_pois:
            if poi.resized_pictures:
                self.sync_media_file(lang, poi.resized_pictures[0][1])
            for picture, resized in poi.resized_pictures[1:]:
                self.sync_media_file(lang, resized)
            for other_file in poi.files:
                self.sync_media_file(lang, other_file.attachment_file)
        if self.with_events:
            self.sync_dive_touristicevents(lang, dive)
        if self.categories:
            self.sync_dive_touristiccontents(lang, dive)
        if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
            self.sync_dive_sensitiveareas(lang, dive)

    def sync_sensitiveareas(self, lang):
        self.sync_geojson(lang, sensitivity_views.SensitiveAreaViewSet, 'sensitiveareas.geojson',
                          params={'practices': 'Terrestre'})
        for area in sensitivity_models.SensitiveArea.objects.existing().filter(published=True):
            name = os.path.join('api', lang, 'sensitiveareas', '{obj.pk}.kml'.format(obj=area))
            self.sync_view(lang, sensitivity_views.SensitiveAreaKMLDetail.as_view(), name, pk=area.pk)
            self.sync_media_file(lang, area.species.pictogram)

    def sync_trek_sensitiveareas(self, lang, trek):
        params = {'format': 'geojson', 'practices': 'Terrestre'}

        view = sensitivity_views.TrekSensitiveAreaViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'sensitiveareas.geojson')
        self.sync_view(lang, view, name, params=params, pk=trek.pk)

    def sync_dive_sensitiveareas(self, lang, dive):
        params = {'format': 'geojson', 'practices': 'Terrestre'}

        view = sensitivity_views.DiveSensitiveAreaViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'sensitiveareas.geojson')
        self.sync_view(lang, view, name, params=params, pk=dive.pk)

    def sync_dives(self, lang):
        self.sync_geojson(lang, diving_views.DiveViewSet, 'dives.geojson')

        dives = diving_models.Dive.objects.existing().order_by('pk')
        dives = dives.filter(**{'published_{lang}'.format(lang=lang): True})

        if self.source:
            dives = dives.filter(source__name__in=self.source)

        if self.portal:
            dives = dives.filter(Q(portal__name__in=self.portal) | Q(portal=None))

        for dive in dives:
            self.sync_dive(lang, dive)

    def sync_tourism(self, lang):
        self.sync_geojson(lang, tourism_views.TouristicContentViewSet, 'touristiccontents.geojson')
        self.sync_geojson(lang, tourism_views.TouristicEventViewSet, 'touristicevents.geojson',
                          params={'ends_after': timezone.now().strftime('%Y-%m-%d')})

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

        if self.portal:
            contents = contents.filter(Q(portal__name__in=self.portal) | Q(portal=None))

        for content in contents:
            self.sync_content(lang, content)

        events = tourism_models.TouristicEvent.objects.existing().order_by('pk')
        events = events.filter(**{'published_{lang}'.format(lang=lang): True})

        if self.source:
            events = events.filter(source__name__in=self.source)

        if self.portal:
            events = events.filter(Q(portal__name__in=self.portal) | Q(portal=None))

        for event in events:
            self.sync_event(lang, event)

        # Information desks
        self.sync_geojson(lang, tourism_views.InformationDeskViewSet, 'information_desks.geojson')
        for pk in tourism_models.InformationDeskType.objects.values_list('pk', flat=True):
            name = 'information_desks-{}.geojson'.format(pk)
            self.sync_geojson(lang, tourism_views.InformationDeskViewSet, name, type=pk)
        for desk in tourism_models.InformationDesk.objects.all():
            self.sync_media_file(lang, desk.thumbnail)

    def sync_trek_touristiccontents(self, lang, trek, zipfile=None):
        params = {'format': 'geojson',
                  'categories': ','.join(category for category in self.categories)}
        if self.portal:
            params['portal'] = ','.join(portal for portal in self.portal)

        view = tourism_views.TrekTouristicContentViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'touristiccontents.geojson')
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

        for content in trek.touristic_contents.all():
            self.sync_touristiccontent_media(lang, content, zipfile=self.trek_zipfile)

    def sync_trek_touristicevents(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        if self.portal:
            params['portal'] = ','.join(portal for portal in self.portal)
        view = tourism_views.TrekTouristicEventViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'touristicevents.geojson')
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=trek.pk)

        for event in trek.touristic_events.all():
            self.sync_touristicevent_media(lang, event, zipfile=self.trek_zipfile)

    def sync_dive_touristiccontents(self, lang, dive):
        params = {'format': 'geojson',
                  'categories': ','.join(category for category in self.categories)}
        if self.portal:
            params['portal'] = ','.join(portal for portal in self.portal)

        view = tourism_views.DiveTouristicContentViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'touristiccontents.geojson')
        self.sync_view(lang, view, name, params=params, pk=dive.pk)

        for content in dive.touristic_contents.all():
            self.sync_touristiccontent_media(lang, content)

    def sync_dive_touristicevents(self, lang, dive):
        params = {'format': 'geojson'}
        if self.portal:
            params['portal'] = ','.join(portal for portal in self.portal)
        view = tourism_views.DiveTouristicEventViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'dives', str(dive.pk), 'touristicevents.geojson')
        self.sync_view(lang, view, name, params=params, pk=dive.pk)

        for event in dive.touristic_events.all():
            self.sync_touristicevent_media(lang, event)

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
        self.sync_tiles()

        step_value = int(50 / len(settings.MODELTRANSLATION_LANGUAGES))
        current_value = 30

        for lang in self.languages:
            if self.celery_task:
                self.celery_task.update_state(
                    state='PROGRESS',
                    meta={
                        'name': self.celery_task.name,
                        'current': current_value + step_value,
                        'total': 100,
                        'infos': "{} : {} ...".format(_("Language"), lang)
                    }
                )
                current_value = current_value + step_value

            translation.activate(lang)
            self.sync_trekking(lang)
            translation.deactivate()

        self.sync_static_file('**', 'tourism/touristicevent.svg')
        self.sync_pictograms('**', tourism_models.InformationDeskType)
        self.sync_pictograms('**', tourism_models.TouristicContentCategory)
        self.sync_pictograms('**', tourism_models.TouristicContentType)
        self.sync_pictograms('**', tourism_models.TouristicEventType)

    def change_pdf_booklet(self, name_1):
        from pdfimpose import options
        import pdfimpose
        arguments = options.process_options(['--size', '2x1', name_1])
        new_pdf = pdfimpose._legacy_pypdf_impose(
            matrix=pdfimpose.ImpositionMatrix(arguments["fold"], arguments["bind"]),
            pages=arguments["pages"],
            last=arguments["last"]
        )
        with open(name_1, "wb") as outfile:
            new_pdf.write(outfile)

    def check_dst_root_is_empty(self):
        if not os.path.exists(self.dst_root):
            return
        existing = set([os.path.basename(p) for p in os.listdir(self.dst_root)])
        remaining = existing - set(('api', 'media', 'meta', 'static', 'zip'))
        if remaining:
            raise CommandError("Destination directory contains extra data")

    def rename_root(self):
        if os.path.exists(self.dst_root):
            tmp_root2 = os.path.join(os.path.dirname(self.dst_root), 'deprecated_sync_rando')
            os.rename(self.dst_root, tmp_root2)
            os.rename(self.tmp_root, self.dst_root)
            shutil.rmtree(tmp_root2)
        else:
            os.rename(self.tmp_root, self.dst_root)

    def handle(self, *args, **options):
        self.successfull = True
        self.verbosity = options['verbosity']
        self.dst_root = options["path"].rstrip('/')
        self.check_dst_root_is_empty()
        url = options['url']
        if url.startswith('https://'):
            self.secure = True
        elif url.startswith('http://'):
            self.secure = False
        else:
            raise CommandError('url parameter should start with http:// or https://')
        self.referer = options['url']
        self.host = self.referer.split('://')[1]
        self.rando_url = options['rando_url']
        if self.rando_url.endswith('/'):
            self.rando_url = self.rando_url[:-1]
        self.factory = RequestFactory()
        self.skip_pdf = options['skip_pdf']
        self.skip_tiles = options['skip_tiles']
        self.skip_dem = options['skip_dem']
        self.skip_profile_png = options['skip_profile_png']
        self.source = options['source']
        if options['languages']:
            for language in options['languages'].split(','):
                if language not in settings.MODELTRANSLATION_LANGUAGES:
                    raise CommandError("Language {lang_n} doesn't exist. Select in these one : {langs}".
                                       format(lang_n=language, langs=settings.MODELTRANSLATION_LANGUAGES))
            self.languages = options['languages'].split(',')
        else:
            self.languages = settings.MODELTRANSLATION_LANGUAGES
        self.with_events = options.get('with_events', False)
        self.categories = None
        if options.get('content_categories', ""):
            self.categories = options.get('content_categories', "").split(',')
        self.with_signages = options.get('with_signages', False)
        self.with_infrastructures = options.get('with_infrastructures', False)
        self.with_dives = options.get('with_dives', False)
        self.celery_task = options.get('task', None)

        if self.source is not None:
            self.source = self.source.split(',')

        if options['portal'] is not None:
            self.portal = options['portal'].split(',')

        else:
            self.portal = []

        if isinstance(settings.MOBILE_TILES_URL, str):
            tiles_url = settings.MOBILE_TILES_URL
        else:
            tiles_url = settings.MOBILE_TILES_URL[0]
        self.builder_args = {
            'tiles_url': tiles_url,
            'tiles_headers': {"Referer": self.referer},
            'ignore_errors': True,
            'tiles_dir': os.path.join(settings.VAR_DIR, 'tiles'),
        }
        self.tmp_root = os.path.join(os.path.dirname(self.dst_root), 'tmp_sync_rando')
        try:
            os.mkdir(self.tmp_root)
        except OSError as e:
            if e.errno != 17:
                raise
            raise CommandError(
                "The {}/ directory already exists. Please check no other sync_rando command is already running."
                " If not, please delete this directory.".format(self.tmp_root)
            )
        try:
            self.sync()
            if self.celery_task:
                self.celery_task.update_state(
                    state='PROGRESS',
                    meta={
                        'name': self.celery_task.name,
                        'current': 100,
                        'total': 100,
                        'infos': "{}".format(_("Sync ended"))
                    }
                )
        except Exception:
            shutil.rmtree(self.tmp_root)
            raise

        self.rename_root()

        done_message = 'Done'
        if self.successfull:
            done_message = self.style.SUCCESS(done_message)

        if self.verbosity >= 1:
            self.stdout.write(done_message)

        if not self.successfull:
            raise CommandError('Some errors raised during synchronization.')

        sleep(2)  # end sleep to ensure sync page get result
