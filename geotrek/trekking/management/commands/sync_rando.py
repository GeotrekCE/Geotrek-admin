from landez import TilesManager
from landez.sources import DownloadError
import logging
from optparse import make_option
import os
import re
import shutil
import tempfile
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.management.base import BaseCommand, CommandError
from django.test.client import RequestFactory
from django.utils import translation

# Workaround https://code.djangoproject.com/ticket/22865
from geotrek.common.models import FileType  # NOQA

from geotrek.altimetry.views import ElevationProfile, ElevationArea, serve_elevation_chart
from geotrek.common import models as common_models
from geotrek.trekking import models as trekking_models
from geotrek.common.views import DocumentPublicPDF
from geotrek.trekking.views import TrekViewSet, POIViewSet, TrekGPXDetail, TrekKMLDetail
from geotrek.flatpages.views import FlatPageViewSet


logger = logging.getLogger(__name__)


class ZipTilesBuilder(object):
    def __init__(self, filepath, close_zip, **builder_args):
        builder_args['tile_format'] = self.format_from_url(builder_args['tiles_url'])
        self.close_zip = close_zip
        self.zipfile = ZipFile(filepath, 'w')
        self.tm = TilesManager(**builder_args)
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
            name = '{0}/{1}/{2}.png'.format(*tile)
            try:
                data = self.tm.tile(tile)
            except DownloadError:
                logger.warning("Failed to download tile %s" % name)
            else:
                self.zipfile.writestr(name, data)
        self.close_zip(self.zipfile)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--url', '-u', action='store', dest='url',
                    default='http://localhost', help='Base url'),
        make_option('--skip-pdf', '-p', action='store_true', dest='skip_pdf',
                    default=False, help='Skip generation of PDF files'),
        make_option('--skip-tiles', '-t', action='store_true', dest='skip_tiles',
                    default=False, help='Skip generation of zip tiles files'),
        make_option('--skip-zip', '-z', action='store_true', dest='skip_zip',
                    default=False, help='Skip generation of zip files for mobile app'),
    )

    def mkdirs(self, name):
        dirname = os.path.dirname(name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def sync_global_tiles(self):
        """ Creates a tiles file on the global extent.
        """
        if self.verbosity == '2':
            self.stdout.write(u"\x1b[36m**\x1b[0m \x1b[1mzip/tiles.zip\x1b[0m ...", ending="")
            self.stdout.flush()

        global_extent = settings.LEAFLET_CONFIG['SPATIAL_EXTENT']

        logger.info("Global extent is %s" % unicode(global_extent))
        global_file = os.path.join(self.tmp_root, 'zip', 'tiles.zip')

        logger.info("Build global tiles file...")
        self.mkdirs(global_file)

        def close_zip(zipfile):
            return self.close_zip(zipfile, 'zip/tiles.zip')

        tiles = ZipTilesBuilder(global_file, close_zip, **self.builder_args)
        tiles.add_coverage(bbox=global_extent,
                           zoomlevels=settings.MOBILE_TILES_GLOBAL_ZOOMS)
        tiles.run()

        if self.verbosity == '2':
            self.stdout.write(u"\x1b[3Dzipped")

    def sync_trek_tiles(self, trek):
        """ Creates a tiles file for the specified Trek object.
        """
        if self.verbosity == '2':
            self.stdout.write(u"\x1b[36m**\x1b[0m \x1b[1mzip/tiles-{pk}.zip\x1b[0m ...".format(pk=trek.pk), ending="")
            self.stdout.flush()

        trek_file = os.path.join(self.tmp_root, 'zip', 'tiles-%s.zip' % trek.id)

        def _radius2bbox(lng, lat, radius):
            return (lng - radius, lat - radius,
                    lng + radius, lat + radius)

        self.mkdirs(trek_file)

        def close_zip(zipfile):
            return self.close_zip(zipfile, 'zip/tiles-%s.zip' % trek.id)

        tiles = ZipTilesBuilder(trek_file, close_zip, **self.builder_args)

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

        if self.verbosity == '2':
            self.stdout.write(u"\x1b[3Dzipped")

    def sync_view(self, lang, view, name, url='/', zipfile=None, **kwargs):
        if self.verbosity == '2':
            self.stdout.write(u"\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m ...".format(lang=lang, name=name), ending="")
            self.stdout.flush()
        fullname = os.path.join(self.tmp_root, name)
        self.mkdirs(fullname)
        request = self.factory.get(url, HTTP_HOST=self.host)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang
        request.user = AnonymousUser()
        response = view(request, **kwargs)
        if hasattr(response, 'render'):
            response.render()
        if response.status_code != 200:
            raise CommandError('Failed to get {name} (status {code})'.format(name=name, code=response.status_code))
        f = open(fullname, 'w')
        f.write(response.content)
        f.close()
        if zipfile:
            zipfile.write(fullname, name)
        if self.verbosity == '2':
            self.stdout.write(u"\x1b[3Dgenerated")

    def sync_geojson(self, lang, viewset, name, zipfile=None):
        view = viewset.as_view({'get': 'list'})
        name = os.path.join('api', lang, '{name}.geojson'.format(name=name))
        self.sync_view(lang, view, name, url='/?format=geojson', zipfile=zipfile)

    def sync_trek_pois(self, lang, trek, zipfile=None):
        view = POIViewSet.as_view({'get': 'list'})
        name = os.path.join('api', lang, 'treks', str(trek.pk), 'pois.geojson')
        self.sync_view(lang, view, name, url='/?format=geojson', zipfile=zipfile, pk=trek.pk)

    def sync_object_view(self, lang, obj, view, basename_fmt, zipfile=None, **kwargs):
        modelname = obj._meta.model_name
        name = os.path.join('api', lang, '{modelname}s'.format(modelname=modelname), str(obj.pk), basename_fmt.format(obj=obj))
        self.sync_view(lang, view, name, zipfile=zipfile, pk=obj.pk, **kwargs)

    def sync_pdf(self, lang, obj):
        if self.skip_pdf:
            return
        view = DocumentPublicPDF.as_view(model=type(obj))
        self.sync_object_view(lang, obj, view, '{obj.slug}.pdf')

    def sync_profile_json(self, lang, obj, zipfile=None):
        view = ElevationProfile.as_view(model=type(obj))
        self.sync_object_view(lang, obj, view, 'profile.json', zipfile=zipfile)

    def sync_profile_png(self, lang, obj, zipfile=None):
        view = serve_elevation_chart
        model_name = type(obj)._meta.model_name
        self.sync_object_view(lang, obj, view, 'profile.png', zipfile=zipfile, model_name=model_name)

    def sync_dem(self, lang, obj):
        view = ElevationArea.as_view(model=type(obj))
        self.sync_object_view(lang, obj, view, 'dem.json')

    def sync_gpx(self, lang, obj):
        self.sync_object_view(lang, obj, TrekGPXDetail.as_view(), '{obj.slug}.gpx')

    def sync_kml(self, lang, obj):
        self.sync_object_view(lang, obj, TrekKMLDetail.as_view(), '{obj.slug}.kml')

    def sync_file(self, lang, name, src_root, url, zipfile=None):
        url = url.strip('/')
        src = os.path.join(src_root, name)
        dst = os.path.join(self.tmp_root, url, name)
        self.mkdirs(dst)
        shutil.copyfile(src, dst)
        if zipfile:
            zipfile.write(dst, os.path.join(url, name))
        if self.verbosity == '2':
            self.stdout.write(u"\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m copied".format(lang=lang, name=name))

    def sync_static_file(self, lang, name):
        self.sync_file(lang, name, settings.STATIC_ROOT, settings.STATIC_URL)

    def sync_media_file(self, lang, field, zipfile=None):
        if field and field.name:
            self.sync_file(lang, field.name, settings.MEDIA_ROOT, settings.MEDIA_URL, zipfile=zipfile)

    def sync_pictograms(self, lang, model, zipfile=None):
        for obj in model.objects.exclude(pictogram=''):
            self.sync_media_file(lang, obj.pictogram, zipfile=zipfile)

    def sync_trek(self, lang, trek):
        zipname = os.path.join('zip', lang, 'trek-%s.zip' % trek.pk)
        zipfullname = os.path.join(self.tmp_root, zipname)
        self.mkdirs(zipfullname)
        self.trek_zipfile = ZipFile(zipfullname, 'w')

        self.sync_trek_pois(lang, trek, zipfile=self.zipfile)
        self.sync_gpx(lang, trek)
        self.sync_kml(lang, trek)
        self.sync_pdf(lang, trek)
        self.sync_profile_json(lang, trek)
        self.sync_profile_png(lang, trek, zipfile=self.zipfile)
        self.sync_dem(lang, trek)
        for desk in trek.information_desks.all():
            self.sync_media_file(lang, desk.thumbnail, zipfile=self.trek_zipfile)
        for poi in trek.published_pois:
            if poi.resized_pictures:
                self.sync_media_file(lang, poi.resized_pictures[0][1], zipfile=self.trek_zipfile)
            for picture, resized in poi.resized_pictures[1:]:
                self.sync_media_file(lang, resized)
        for picture, resized in trek.resized_pictures:
            self.sync_media_file(lang, resized, zipfile=self.trek_zipfile)

        self.close_zip(self.trek_zipfile, zipname)

        if self.verbosity == '2':
            self.stdout.write(u"\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m zipped".format(lang=lang, name=zipname))

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
            logger.info('%s was up to date.' % zipfilename)
        else:
            logger.info('%s was NOT up to date.' % zipfilename)

    def sync_trekking(self, lang):
        zipname = os.path.join('zip', lang, 'treks.zip')
        zipfullname = os.path.join(self.tmp_root, zipname)
        self.mkdirs(zipfullname)
        self.zipfile = ZipFile(zipfullname, 'w')

        self.sync_geojson(lang, TrekViewSet, 'treks', zipfile=self.zipfile)
        self.sync_geojson(lang, POIViewSet, 'pois')
        self.sync_geojson(lang, FlatPageViewSet, 'flatpages', zipfile=self.zipfile)
        self.sync_static_file(lang, 'trekking/trek.svg')
        self.sync_pictograms(lang, common_models.Theme, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.TrekNetwork, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.Practice, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.Accessibility, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.DifficultyLevel, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.POIType, zipfile=self.zipfile)
        self.sync_pictograms(lang, trekking_models.Route)
        self.sync_pictograms(lang, trekking_models.WebLinkCategory)

        treks = trekking_models.Trek.objects.existing()
        treks = treks.filter(**{'published_{lang}'.format(lang=lang): True})

        for trek in treks:
            self.sync_trek(lang, trek)

        self.close_zip(self.zipfile, zipname)

        if self.verbosity == '2':
            self.stdout.write(u"\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m zipped".format(lang=lang, name=zipname))

    def sync_tiles(self):
        if self.skip_tiles:
            return
        self.sync_global_tiles()
        for trek in trekking_models.Trek.objects.existing().order_by('pk'):
            if trek.any_published:
                self.sync_trek_tiles(trek)

    def sync(self):
        self.sync_tiles()

        for lang in settings.MODELTRANSLATION_LANGUAGES:
            self.sync_trekking(lang)

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity', '1')
        if len(args) < 1:
            raise CommandError(u"Missing parameter destination directory")
        self.dst_root = args[0]
        if os.path.exists(self.dst_root):
            existing = set([os.path.basename(p) for p in os.listdir(self.dst_root)])
            remaining = existing - set(('api', 'media', 'static', 'zip'))
            if remaining:
                raise CommandError(u"Destination directory contains extra data")
        if(options['url'][:7] != 'http://'):
            raise CommandError('url parameter should start with http://')
        self.referer = options['url']
        self.host = self.referer[7:]
        self.factory = RequestFactory()
        self.tmp_root = tempfile.mkdtemp('_sync_rando', dir=os.path.dirname(self.dst_root))
        self.skip_pdf = options['skip_pdf']
        self.skip_tiles = options['skip_tiles']
        self.builder_args = {
            'tiles_url': settings.MOBILE_TILES_URL,
            'tiles_headers': {"Referer": self.referer},
            'ignore_errors': True,
            'tiles_dir': os.path.join(settings.CACHE_ROOT, 'tiles'),
        }

        try:
            self.sync()
        except:
            shutil.rmtree(self.tmp_root)
            raise

        if os.path.exists(self.dst_root):
            tmp_root2 = tempfile.mkdtemp('_sync_rando', dir=os.path.dirname(self.dst_root))
            os.rename(self.dst_root, os.path.join(tmp_root2, 'to_delete'))
            os.rename(self.tmp_root, self.dst_root)
            shutil.rmtree(tmp_root2)
        else:
            os.rename(self.tmp_root, self.dst_root)

        if self.verbosity >= '1':
            self.stdout.write('Done')
