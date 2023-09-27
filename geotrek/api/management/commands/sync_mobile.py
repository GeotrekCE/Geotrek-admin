import argparse
import logging
import filecmp
import os
import stat
from PIL import Image
import re
import shutil
import tempfile
from time import sleep
from zipfile import ZipFile
import cairosvg

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.test.client import RequestFactory
from django.utils import translation
from django.utils.translation import gettext as _
from geotrek.common.models import FileType  # NOQA
from geotrek.common import models as common_models
from geotrek.common.functions import GeometryType
from geotrek.flatpages.models import FlatPage
from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models
from geotrek.api.mobile.views.trekking import TrekViewSet
from geotrek.api.mobile.views.common import FlatPageViewSet, SettingsView
from geotrek.common.helpers_sync import ZipTilesBuilder
# Register mapentity models
from geotrek.trekking import urls  # NOQA
from geotrek.tourism import urls  # NOQA


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('--empty-tmp-folder', dest='empty_tmp_folder', action='store_true', default=False,
                            help='Empty tmp folder')
        parser.add_argument('--languages', '-l', dest='languages', default='', help='Languages to sync')
        parser.add_argument('--portal', '-P', dest='portal', default=None, help='Filter by portal(s)')
        parser.add_argument('--skip-tiles', '-t', action='store_true', dest='skip_tiles', default=False,
                            help='Skip inclusion of tiles in zip files')
        parser.add_argument('--url', '-u', dest='url', default='http://localhost', help='Base url')
        parser.add_argument('--indent', '-i', default=0, type=int, help='Indent json files')
        parser.add_argument('--task', default=None, help=argparse.SUPPRESS)

    def mkdirs(self, name):
        dirname = os.path.dirname(name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def sync_view(self, lang, view, name, url='/', params=None, headers={}, zipfile=None, fix2028=False, **kwargs):
        if self.verbosity == 2:
            self.stdout.write("\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m ...".format(lang=lang, name=name), ending="")
            self.stdout._out.flush()
        fullname = os.path.join(self.tmp_root, name)
        self.mkdirs(fullname)
        request = self.factory.get(url, params, **headers)
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
            return
        if response.status_code != 200:
            self.successfull = False
            if self.verbosity == 2:
                self.stdout.write("\x1b[3D\x1b[31;1mfailed (HTTP {code})\x1b[0m".format(code=response.status_code))
            return
        f = open(fullname, 'wb')
        if isinstance(response, StreamingHttpResponse):
            content = b''.join(response.streaming_content)
        else:
            content = response.content
        # Fix strange unicode characters 2028 and 2029 that make Geotrek-mobile crash
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
                self.stdout.write("\x1b[3D\x1b[32munchanged\x1b[0m")
        else:
            if self.verbosity == 2:
                self.stdout.write("\x1b[3D\x1b[32mgenerated\x1b[0m")

    def sync_json(self, lang, viewset, name, zipfile=None, params={}, as_view_args=[], **kwargs):
        view = viewset.as_view(*as_view_args)
        name = os.path.join(lang, '{name}.json'.format(name=name))
        params = params.copy()
        if self.portal:
            params['portal'] = ','.join(self.portal)
        headers = {}
        if self.indent:
            headers['HTTP_ACCEPT'] = 'application/json; indent={}'.format(self.indent)
        self.sync_view(lang, view, name, params=params, headers=headers, zipfile=zipfile, fix2028=True, **kwargs)

    def sync_geojson(self, lang, viewset, name, zipfile=None, params={}, type_view={}, **kwargs):
        view = viewset.as_view(type_view)
        name = os.path.join(lang, name)
        params = params.copy()
        params.update({'format': 'geojson'})

        if self.portal:
            params['portal'] = ','.join(self.portal)

        headers = {}
        if self.indent:
            headers['HTTP_ACCEPT'] = 'application/geo+json; indent={}'.format(self.indent)

        self.sync_view(lang, view, name, params=params, headers=headers, zipfile=zipfile, fix2028=True, **kwargs)

    def sync_trek_pois(self, lang, trek):
        params = {'format': 'geojson', 'root_pk': trek.pk}
        view = TrekViewSet.as_view({'get': 'pois'})
        name = os.path.join(lang, str(trek.pk), 'pois.geojson')
        self.sync_view(lang, view, name, params=params, pk=trek.pk)
        # Sync POIs of children too
        for child in trek.children.annotate(geom_type=GeometryType("geom")).filter(geom_type="LINESTRING"):
            name = os.path.join(lang, str(trek.pk), 'pois', '{}.geojson'.format(child.pk))
            self.sync_view(lang, view, name, params=params, pk=child.pk)

    def sync_trek_touristic_contents(self, lang, trek):
        params = {'format': 'geojson', 'root_pk': trek.pk}
        if self.portal:
            params['portal'] = ','.join(self.portal)
        view = TrekViewSet.as_view({'get': 'touristic_contents'})
        name = os.path.join(lang, str(trek.pk), 'touristic_contents.geojson')
        self.sync_view(lang, view, name, params=params, pk=trek.pk)
        # Sync contents of children too
        for child in trek.children.annotate(geom_type=GeometryType("geom")).filter(geom_type="LINESTRING"):
            name = os.path.join(lang, str(trek.pk), 'touristic_contents', '{}.geojson'.format(child.pk))
            self.sync_view(lang, view, name, params=params, pk=child.pk)

    def sync_trek_touristic_events(self, lang, trek):
        params = {'format': 'geojson', 'root_pk': trek.pk}
        if self.portal:
            params['portal'] = ','.join(self.portal)
        view = TrekViewSet.as_view({'get': 'touristic_events'})
        name = os.path.join(lang, str(trek.pk), 'touristic_events.geojson')
        self.sync_view(lang, view, name, params=params, pk=trek.pk)
        # Sync events of children too
        for child in trek.children.annotate(geom_type=GeometryType("geom")).filter(geom_type="LINESTRING"):
            name = os.path.join(lang, str(trek.pk), 'touristic_events', '{}.geojson'.format(child.pk))
            self.sync_view(lang, view, name, params=params, pk=child.pk)

    def sync_file(self, name, src_root, url, directory='', zipfile=None):
        url = url.strip('/')
        src = os.path.join(src_root, name)
        dst = os.path.join(self.tmp_root, directory, url, name)
        self.mkdirs(dst)
        if not os.path.isfile(dst):
            os.link(src, dst)
        if zipfile and os.path.join(url, name) not in zipfile.namelist():
            zipfile.write(dst, os.path.join(url, name))
        if self.verbosity == 2:
            self.stdout.write(
                "\x1b[36m**\x1b[0m \x1b[1m{directory}/{url}/{name}\x1b[0m \x1b[32mcopied\x1b[0m".format(
                    directory=directory, url=url, name=name))

    def sync_media_file(self, field, prefix=None, directory='', zipfile=None):
        if field and field.name:
            url_media = '/%s%s' % (prefix, settings.MEDIA_URL) if prefix else settings.MEDIA_URL
            self.sync_file(field.name, settings.MEDIA_ROOT, url_media, directory=directory, zipfile=zipfile)

    def sync_pictograms(self, model, directory='', zipfile=None, size=None):
        for obj in model.objects.all():
            if not obj.pictogram:
                continue
            file_name, file_extension = os.path.splitext(obj.pictogram.name)
            if file_extension == '.svg':
                name = os.path.join(settings.MEDIA_URL.strip('/'), '%s.png' % file_name)
            else:
                name = os.path.join(settings.MEDIA_URL.strip('/'), obj.pictogram.name)
            dst = os.path.join(self.tmp_root, directory, name)
            self.mkdirs(dst)
            # Convert SVG to PNG and open it
            if file_extension == '.svg':
                cairosvg.svg2png(url=obj.pictogram.path, write_to=dst)
                image = Image.open(dst)
            else:
                image = Image.open(obj.pictogram.path)
            # Resize
            if size:
                image = image.resize((size, size), Image.Resampling.LANCZOS)
            # Save
            image.save(dst, optimize=True, quality=95)
            if name not in zipfile.namelist():
                zipfile.write(dst, name)
            if self.verbosity == 2:
                self.stdout.write(
                    "\x1b[36m**\x1b[0m \x1b[1m{directory}{url}/{name}\x1b[0m \x1b[32mcopied\x1b[0m".format(
                        directory=directory, url=obj.pictogram.url, name=name))

    def close_zip(self, zipfile, name):
        if self.verbosity == 2:
            self.stdout.write("\x1b[36m**\x1b[0m \x1b[1m{name}\x1b[0m ...".format(name=name), ending="")
            self.stdout._out.flush()

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
                self.stdout.write("\x1b[3D\x1b[32munchanged\x1b[0m")
            else:
                self.stdout.write("\x1b[3D\x1b[32mzipped\x1b[0m")

    def sync_flatpage(self, lang):
        flatpages = FlatPage.objects.order_by('pk').filter(target__in=['mobile', 'all']).filter(
            **{'published_{lang}'.format(lang=lang): True})
        if self.portal:
            flatpages = flatpages.filter(Q(portal__name__in=self.portal) | Q(portal=None))
        self.sync_json(lang, FlatPageViewSet, 'flatpages',
                       as_view_args=[{'get': 'list'}])
        for flatpage in flatpages:
            self.sync_json(lang, FlatPageViewSet, 'flatpages/{pk}'.format(pk=flatpage.pk), pk=flatpage.pk,
                           as_view_args=[{'get': 'retrieve'}])

    def sync_trekking(self, lang):
        self.sync_geojson(lang, TrekViewSet, 'treks.geojson', type_view={'get': 'list'})
        treks = trekking_models.Trek.objects.annotate(geom_type=GeometryType("geom")).filter(geom_type="LINESTRING").existing().order_by('pk')
        treks = treks.filter(**{'published_{lang}'.format(lang=lang): True})

        if self.portal:
            treks = treks.filter(Q(portal__name__in=self.portal) | Q(portal=None))

        for trek in treks:
            self.sync_geojson(lang, TrekViewSet, '{pk}/trek.geojson'.format(pk=trek.pk), pk=trek.pk,
                              type_view={'get': 'retrieve'})
            self.sync_trek_pois(lang, trek)
            self.sync_trek_touristic_contents(lang, trek)
            self.sync_trek_touristic_events(lang, trek)
            # Sync detail of children too
            for child in trek.children.annotate(geom_type=GeometryType("geom")).filter(geom_type="LINESTRING"):
                self.sync_geojson(
                    lang, TrekViewSet,
                    '{pk}/treks/{child_pk}.geojson'.format(pk=trek.pk, child_pk=child.pk),
                    pk=child.pk, type_view={'get': 'retrieve'}, params={'root_pk': trek.pk},
                )

    def sync_settings_json(self, lang):
        self.sync_json(lang, SettingsView, 'settings')

    def sync_medias(self):
        if self.celery_task:
            self.celery_task.update_state(
                state='PROGRESS',
                meta={
                    'name': self.celery_task.name,
                    'current': 10,
                    'total': 100,
                    'infos': "{}".format(_("Medias syncing ..."))
                }
            )
        self.sync_global_media()
        self.sync_treks_media()

    def sync_trek_by_pk_media(self, trek):
        url_trek = os.path.join('nolang')
        zipname_trekid = os.path.join(url_trek, "{}.zip".format(trek.pk))
        zipfullname_trekid = os.path.join(self.tmp_root, zipname_trekid)
        self.mkdirs(zipfullname_trekid)
        trekid_zipfile = ZipFile(zipfullname_trekid, 'w')

        if not self.skip_tiles:
            self.sync_trek_tiles(trek, trekid_zipfile)

        for poi in trek.published_pois.annotate(geom_type=GeometryType("geom")).filter(geom_type="POINT"):
            if poi.resized_pictures:
                for picture, thdetail in poi.resized_pictures[:settings.MOBILE_NUMBER_PICTURES_SYNC]:
                    self.sync_media_file(thdetail, prefix=trek.pk, directory=url_trek,
                                         zipfile=trekid_zipfile)
        for touristic_content in trek.published_touristic_contents.annotate(geom_type=GeometryType("geom")).filter(geom_type="POINT"):
            if touristic_content.resized_pictures:
                for picture, thdetail in touristic_content.resized_pictures[:settings.MOBILE_NUMBER_PICTURES_SYNC]:
                    self.sync_media_file(thdetail, prefix=trek.pk, directory=url_trek,
                                         zipfile=trekid_zipfile)
        for touristic_event in trek.published_touristic_events.annotate(geom_type=GeometryType("geom")).filter(geom_type="POINT"):
            if touristic_event.resized_pictures:
                for picture, thdetail in touristic_event.resized_pictures[:settings.MOBILE_NUMBER_PICTURES_SYNC]:
                    self.sync_media_file(thdetail, prefix=trek.pk, directory=url_trek,
                                         zipfile=trekid_zipfile)
        if trek.resized_pictures:
            for picture, thdetail in trek.resized_pictures[:settings.MOBILE_NUMBER_PICTURES_SYNC]:
                self.sync_media_file(thdetail, prefix=trek.pk, directory=url_trek,
                                     zipfile=trekid_zipfile)
        for desk in trek.information_desks.all().annotate(geom_type=GeometryType("geom")).filter(geom_type="POINT"):
            if desk.resized_picture:
                self.sync_media_file(desk.resized_picture, prefix=trek.pk, directory=url_trek,
                                     zipfile=trekid_zipfile)
        for lang in self.languages:
            trek.prepare_elevation_chart(lang, self.referer)
            url_media = '/{}{}'.format(trek.pk, settings.MEDIA_URL)
            self.sync_file(trek.get_elevation_chart_url_png(lang), settings.MEDIA_ROOT,
                           url_media, directory=url_trek, zipfile=trekid_zipfile)
        # Sync media of children too
        for child in trek.children.annotate(geom_type=GeometryType("geom")).filter(geom_type="LINESTRING"):
            for picture, resized in child.resized_pictures:
                self.sync_media_file(resized, prefix=trek.pk, directory=url_trek, zipfile=trekid_zipfile)
            for desk in child.information_desks.all().annotate(geom_type=GeometryType("geom")).filter(geom_type="POINT"):
                self.sync_media_file(desk.resized_picture, prefix=trek.pk, directory=url_trek, zipfile=trekid_zipfile)
            for lang in self.languages:
                child.prepare_elevation_chart(lang, self.referer)
                url_media = '/{}{}'.format(trek.pk, settings.MEDIA_URL)
                self.sync_file(child.get_elevation_chart_url_png(lang), settings.MEDIA_ROOT,
                               url_media, directory=url_trek, zipfile=trekid_zipfile)

        self.close_zip(trekid_zipfile, zipname_trekid)

    def sync_treks_media(self):
        treks = trekking_models.Trek.objects.annotate(geom_type=GeometryType("geom")).filter(geom_type="LINESTRING").existing().filter(published=True).order_by('pk')
        if self.portal:
            treks = treks.filter(Q(portal__name__in=self.portal) | Q(portal=None))

        for trek in treks:
            self.sync_trek_by_pk_media(trek)

    def sync_global_media(self):
        url_media_nolang = os.path.join('nolang')
        zipname_settings = os.path.join('nolang', 'global.zip')
        zipfullname_settings = os.path.join(self.tmp_root, zipname_settings)
        self.mkdirs(zipfullname_settings)
        self.zipfile_settings = ZipFile(zipfullname_settings, 'w')

        if not self.skip_tiles:
            self.sync_global_tiles(self.zipfile_settings)

        self.sync_pictograms(common_models.Theme, directory=url_media_nolang, zipfile=self.zipfile_settings)
        self.sync_pictograms(trekking_models.TrekNetwork, directory=url_media_nolang, zipfile=self.zipfile_settings)
        self.sync_pictograms(trekking_models.Practice, directory=url_media_nolang, zipfile=self.zipfile_settings,
                             size=settings.MOBILE_CATEGORY_PICTO_SIZE)
        self.sync_pictograms(trekking_models.Accessibility, directory=url_media_nolang, zipfile=self.zipfile_settings)
        self.sync_pictograms(trekking_models.DifficultyLevel, directory=url_media_nolang, zipfile=self.zipfile_settings)
        self.sync_pictograms(trekking_models.POIType, directory=url_media_nolang, zipfile=self.zipfile_settings,
                             size=settings.MOBILE_POI_PICTO_SIZE)
        self.sync_pictograms(trekking_models.Route, directory=url_media_nolang, zipfile=self.zipfile_settings)
        self.sync_pictograms(trekking_models.ServiceType, directory=url_media_nolang, zipfile=self.zipfile_settings)
        self.sync_pictograms(tourism_models.InformationDeskType, directory=url_media_nolang,
                             zipfile=self.zipfile_settings, size=settings.MOBILE_INFORMATIONDESKTYPE_PICTO_SIZE)
        self.sync_pictograms(tourism_models.TouristicContentCategory, directory=url_media_nolang,
                             zipfile=self.zipfile_settings, size=settings.MOBILE_CATEGORY_PICTO_SIZE)
        self.sync_pictograms(tourism_models.TouristicContentType, directory=url_media_nolang,
                             zipfile=self.zipfile_settings)
        self.sync_pictograms(tourism_models.TouristicEventType, directory=url_media_nolang,
                             zipfile=self.zipfile_settings)
        self.close_zip(self.zipfile_settings, zipname_settings)

    def sync_trek_tiles(self, trek, zipfile):
        """ Add tiles to zipfile for the specified Trek object.
        """

        if self.verbosity == 2:
            self.stdout.write("\x1b[36m**\x1b[0m \x1b[1mnolang/{}/tiles/\x1b[0m ...".format(trek.pk), ending="")
            self.stdout._out.flush()

        def _radius2bbox(lng, lat, radius):
            return (lng - radius, lat - radius,
                    lng + radius, lat + radius)

        tiles = ZipTilesBuilder(zipfile, prefix='/{}/tiles/'.format(trek.pk), **self.builder_args)

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

        if self.verbosity == 2:
            self.stdout.write("\x1b[3D\x1b[32mdownloaded\x1b[0m")

    def sync_global_tiles(self, zipfile):
        """ Add tiles to zipfile on the global extent.
        """
        if self.verbosity == 2:
            self.stdout.write("\x1b[36m**\x1b[0m \x1b[1mtiles/\x1b[0m ...", ending="")
            self.stdout._out.flush()

        global_extent = settings.LEAFLET_CONFIG['SPATIAL_EXTENT']

        logger.info("Global extent is %s" % str(global_extent))
        logger.info("Build global tiles file...")

        tiles = ZipTilesBuilder(zipfile, prefix='tiles/', **self.builder_args)
        tiles.add_coverage(bbox=global_extent,
                           zoomlevels=settings.MOBILE_TILES_GLOBAL_ZOOMS)
        tiles.run()

        if self.verbosity == 2:
            self.stdout.write("\x1b[3D\x1b[32mdownloaded\x1b[0m")

    def sync(self):
        step_value = int(50 / len(settings.MODELTRANSLATION_LANGUAGES))
        current_value = 30

        self.sync_medias()

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
            self.sync_settings_json(lang)
            if 'geotrek.flatpages' in settings.INSTALLED_APPS:
                self.sync_flatpage(lang)
            self.sync_trekking(lang)
            translation.deactivate()

    def check_dst_root_is_empty(self):
        if not os.path.exists(self.dst_root):
            return
        existing = set([os.path.basename(p) for p in os.listdir(self.dst_root)])
        remaining = existing - {'nolang'} - set(settings.MODELTRANSLATION_LANGUAGES)
        if remaining:
            raise CommandError("Destination directory contains extra data")

    def rename_root(self):
        if os.path.exists(self.dst_root):
            tmp_root2 = os.path.join(os.path.dirname(self.dst_root), 'deprecated_sync_mobile')
            os.rename(self.dst_root, tmp_root2)
            shutil.rmtree(tmp_root2)
        os.rename(self.tmp_root, self.dst_root)
        os.chmod(self.dst_root, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
        os.mkdir(self.tmp_root)  # Recreate otherwise python3.6 will complain it does not find the tmp dir at cleanup.

    def handle(self, *args, **options):
        self.successfull = True
        self.verbosity = options['verbosity']
        self.skip_tiles = options['skip_tiles']
        self.indent = options['indent']
        self.factory = RequestFactory()
        self.dst_root = options["path"].rstrip('/')
        self.abs_path = os.path.abspath(options["path"])
        self.check_dst_root_is_empty()

        if options['languages']:
            for language in options['languages'].split(','):
                if language not in settings.MODELTRANSLATION_LANGUAGES:
                    raise CommandError("Language {lang_n} doesn't exist. Select in these one : {langs}".
                                       format(lang_n=language, langs=settings.MODELTRANSLATION_LANGUAGES))
            self.languages = options['languages'].split(',')
        else:
            self.languages = settings.MODELTRANSLATION_LANGUAGES
        self.celery_task = options.get('task', None)

        if options['portal'] is not None:
            self.portal = options['portal'].split(',')
        else:
            self.portal = []
        url = options['url']
        if not re.search('http[s]?://', url):
            raise CommandError('url parameter should start with http:// or https://')
        self.referer = options['url']
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
        sync_mobile_tmp_dir = os.path.join(settings.TMP_DIR, 'sync_mobile')
        if options['empty_tmp_folder']:
            for dir in os.listdir(sync_mobile_tmp_dir):
                shutil.rmtree(os.path.join(sync_mobile_tmp_dir, dir))
        if not os.path.exists(settings.TMP_DIR):
            os.mkdir(settings.TMP_DIR)
        if not os.path.exists(sync_mobile_tmp_dir):
            os.mkdir(sync_mobile_tmp_dir)

        with tempfile.TemporaryDirectory(dir=sync_mobile_tmp_dir) as tmp_dir:
            self.tmp_root = tmp_dir
            self.sync()
            if self.celery_task:
                self.celery_task.update_state(
                    state='PROGRESS',
                    meta={
                        'name': self.celery_task.name,
                        'current': 100,
                        'total': 100,
                        'infos': "{}".format(_("Sync mobile ended"))
                    }
                )
            self.rename_root()

        done_message = 'Done'
        if self.successfull:
            done_message = self.style.SUCCESS(done_message)

        if self.verbosity >= 1:
            self.stdout.write(done_message)

        if not self.successfull:
            raise CommandError('Some errors raised during synchronization.')

        sleep(2)  # end sleep to ensure sync page get result
