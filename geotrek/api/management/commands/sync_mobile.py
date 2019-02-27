# -*- encoding: UTF-8 -

import logging
import filecmp
import os
import shutil
from time import sleep
from zipfile import ZipFile
import cairosvg
from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.test.client import RequestFactory
from django.utils import translation
from django.utils.translation import ugettext as _
from geotrek.common.models import FileType  # NOQA
from geotrek.common import models as common_models
from geotrek.flatpages.models import FlatPage
from geotrek.trekking import models as trekking_models
from geotrek.api.mobile.views.trekking import (TrekViewSet, POIViewSet)
from geotrek.api.mobile.views.common import FlatPageViewSet, SettingsView
from geotrek.trekking.management.commands.sync_rando import ZipTilesBuilder
# Register mapentity models
from geotrek.trekking import urls  # NOQA
from geotrek.tourism import urls  # NOQA


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('--languages', '-l', dest='languages', default='', help='Languages to sync')
        parser.add_argument('--portal', '-P', dest='portal', default=None, help='Filter by portal(s)')
        parser.add_argument('--skip-tiles', '-t', action='store_true', dest='skip_tiles', default=False,
                            help='Skip generation of zip tiles files')
        parser.add_argument('--url', '-u', dest='url', default='http://localhost', help='Base url')

    def mkdirs(self, name):
        dirname = os.path.dirname(name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def sync_view(self, lang, view, name, url='/', params={}, zipfile=None, fix2028=False, **kwargs):
        if self.verbosity == 2:
            self.stdout.write(u"\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m ...".format(lang=lang, name=name), ending="")
            self.stdout.flush()
        fullname = os.path.join(self.tmp_root, name)
        self.mkdirs(fullname)
        request = self.factory.get(url, params)
        request.LANGUAGE_CODE = lang
        request.user = AnonymousUser()
        try:
            response = view(request, **kwargs)
            if hasattr(response, 'render'):
                response.render()
        except Exception as e:
            self.successfull = False
            if self.verbosity == 2:
                self.stdout.write(u"\x1b[3D\x1b[31mfailed ({})\x1b[0m".format(e))
            return
        if response.status_code != 200:
            self.successfull = False
            if self.verbosity == 2:
                self.stdout.write(u"\x1b[3D\x1b[31;1mfailed (HTTP {code})\x1b[0m".format(code=response.status_code))
            return
        f = open(fullname, 'w')
        if isinstance(response, StreamingHttpResponse):
            content = b''.join(response.streaming_content)
        else:
            content = response.content
        # Fix strange unicode characters 2028 and 2029 that make Geotrek-mobile crash
        if fix2028:
            content = content.replace('\\u2028', '\\n')
            content = content.replace('\\u2029', '\\n')
        f.write(content)
        f.close()
        oldfilename = os.path.join(self.dst_root, name)
        # If new file is identical to old one, don't recreate it. This will help backup
        if os.path.isfile(oldfilename) and filecmp.cmp(fullname, oldfilename):
            os.unlink(fullname)
            os.link(oldfilename, fullname)
            if self.verbosity == 2:
                self.stdout.write(u"\x1b[3D\x1b[32munchanged\x1b[0m")
        else:
            if self.verbosity == 2:
                self.stdout.write(u"\x1b[3D\x1b[32mgenerated\x1b[0m")
        # FixMe: Find why there are duplicate files.
        if zipfile:
            if name not in zipfile.namelist():
                zipfile.write(fullname, name)

    def sync_json(self, lang, viewset, name, zipfile=None, params={}, as_view_args=[], **kwargs):
        view = viewset.as_view(*as_view_args)
        name = os.path.join('mobile', lang, '{name}.json'.format(name=name))
        if self.portal:
            params['portal'] = ','.join(self.portal)
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, fix2028=True, **kwargs)

    def sync_geojson(self, lang, viewset, name, zipfile=None, params={}, type_view={}, **kwargs):
        view = viewset.as_view(type_view)
        name = os.path.join('mobile', lang, name)
        params.update({'format': 'geojson'})

        if self.portal:
            params['portal'] = ','.join(self.portal)

        elif 'portal' in params.keys():
            del params['portal']

        self.sync_view(lang, view, name, params=params, zipfile=zipfile, fix2028=True, **kwargs)

    def sync_trek_pois(self, lang, trek, zipfile=None):
        params = {'format': 'geojson'}
        view = POIViewSet.as_view({'get': 'list'})
        name = os.path.join('mobile', lang, 'treks', str(trek.pk), 'pois.geojson')
        self.sync_view(lang, view, name, params=params, pk=trek.pk)

    def sync_file(self, lang, name, src_root, url, zipfile=None):
        url = url.strip('/')
        src = os.path.join(src_root, name)
        dst = os.path.join(self.tmp_root, url, name)
        self.mkdirs(dst)
        if not os.path.isfile(dst):
            os.link(src, dst)
        if zipfile:
            zipfile.write(dst, os.path.join(url, name))
        os.remove(dst)
        if self.verbosity == 2:
            self.stdout.write(
                u"\x1b[36m{lang}\x1b[0m \x1b[1m{url}/{name}\x1b[0m \x1b[32mcopied\x1b[0m".format(lang=lang,
                                                                                                 url=url,
                                                                                                 name=name))

    def sync_static_file(self, lang, name):
        self.sync_file(lang, name, settings.STATIC_ROOT, settings.STATIC_URL)

    def sync_media_file(self, lang, field, zipfile=None):
        if field and field.name:
            self.sync_file(lang, field.name, settings.MEDIA_ROOT, settings.MEDIA_URL, zipfile=zipfile)

    def sync_pictograms(self, lang, model, zipfile=None):
        for obj in model.objects.all():
            file_name, file_extension = os.path.splitext(str(obj.pictogram))
            if file_extension == '.svg':
                dst = os.path.join(self.tmp_root, settings.MEDIA_URL.strip('/'), '%s.png' % file_name)
                self.mkdirs(dst)
                cairosvg.svg2png(url=obj.pictogram.path, write_to=dst)
                zipfile.write(dst)
            else:
                self.sync_media_file(lang, obj.pictogram, zipfile=zipfile)

    def sync_poi_media(self, lang, poi):
        if poi.resized_pictures:
            self.sync_media_file(lang, poi.resized_pictures[0][1], zipfile=self.trek_zipfile)
        for picture, resized in poi.resized_pictures[1:]:
            self.sync_media_file(lang, resized)
        for other_file in poi.files:
            self.sync_media_file(lang, other_file.attachment_file)

    def sync_trek(self, lang, trek):
        url_trek = os.path.join('mobile', 'common', 'treks')
        zipname = os.path.join(url_trek, '{pk}.zip'.format(pk=trek.pk))
        zipfullname = os.path.join(self.tmp_root, zipname)
        self.mkdirs(zipfullname)
        self.trek_zipfile = ZipFile(zipfullname, 'w')

        self.sync_trek_pois(lang, trek, zipfile=self.trek_zipfile)
        self.sync_media_file(lang, trek.thumbnail_mobile, zipfile=self.trek_zipfile)
        for poi in trek.published_pois:
            self.sync_poi_media(lang, poi)
        for picture, resized in trek.resized_pictures:
            self.sync_media_file(lang, resized, zipfile=self.trek_zipfile)

        if self.verbosity == 2:
            self.stdout.write(u"\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m ...".format(lang=lang, name=zipname),
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
                self.stdout.write(u"\x1b[3D\x1b[32munchanged\x1b[0m")
            else:
                self.stdout.write(u"\x1b[3D\x1b[32mzipped\x1b[0m")

    def sync_common(self, lang):
        zipname_common = os.path.join('mobile', 'common', 'global.zip')
        zipfullname_common = os.path.join(self.tmp_root, zipname_common)
        self.mkdirs(zipfullname_common)
        self.zipfile_common = ZipFile(zipfullname_common, 'w')

        self.sync_json(lang, SettingsView, 'settings', zipfile=self.zipfile_common)

        self.sync_pictograms(lang, common_models.Theme, zipfile=self.zipfile_common)
        self.sync_pictograms(lang, trekking_models.TrekNetwork, zipfile=self.zipfile_common)
        self.sync_pictograms(lang, trekking_models.Practice, zipfile=self.zipfile_common)
        self.sync_pictograms(lang, trekking_models.Accessibility, zipfile=self.zipfile_common)
        self.sync_pictograms(lang, trekking_models.DifficultyLevel, zipfile=self.zipfile_common)
        self.sync_pictograms(lang, trekking_models.POIType, zipfile=self.zipfile_common)
        self.sync_pictograms(lang, trekking_models.Route, zipfile=self.zipfile_common)

    def sync_flatpage(self, lang):
        flatpages = FlatPage.objects.order_by('pk').filter(**{'published_{lang}'.format(lang=lang): True})
        self.sync_json(lang, FlatPageViewSet, 'flatpages',
                       as_view_args=[{'get': 'list'}])
        for flatpage in flatpages:
            self.sync_json(lang, FlatPageViewSet, 'flatpages/{pk}/'.format(pk=flatpage.pk),
                           as_view_args=[{'get': 'retrieve', 'pk': flatpage.pk}])

    def sync_trekking(self, lang):
        zipname_trek = os.path.join('mobile', 'common', 'treks', 'global.zip')
        zipfullname_trek = os.path.join(self.tmp_root, zipname_trek)
        self.mkdirs(zipfullname_trek)
        self.zipfile_trek = ZipFile(zipfullname_trek, 'w')

        self.sync_geojson(lang, TrekViewSet, 'trek.geojson', type_view={'get': 'list'})

        treks = trekking_models.Trek.objects.existing().order_by('pk')
        treks = treks.filter(
            Q(**{'published_{lang}'.format(lang=lang): True})
            | Q(**{'trek_parents__parent__published_{lang}'.format(lang=lang): True,
                   'trek_parents__parent__deleted': False})
        )

        if self.portal:
            treks = treks.filter(Q(portal__name__in=self.portal) | Q(portal=None))

        self.sync_common(lang)
        for trek in treks:
            self.sync_trek(lang, trek)
            self.sync_geojson(lang, TrekViewSet, 'treks/{pk}.geojson'.format(pk=trek.pk), type_view={'get': 'list'})

        if self.verbosity == 2:
            self.stdout.write(u"\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m ...".format(lang=lang, name=zipname_trek),
                              ending="")

        self.close_zip(self.zipfile_trek, zipname_trek)

    def sync_trek_tiles(self, trek):
        """ Creates a tiles file for the specified Trek object.
        """
        zipname = os.path.join('mobile', 'tiles', 'treks', '{pk}.zip'.format(pk=trek.pk))

        if self.verbosity == 2:
            self.stdout.write(u"\x1b[36m**\x1b[0m \x1b[1m{name}\x1b[0m ...".format(name=zipname), ending="")
            self.stdout.flush()

        trek_file = os.path.join(self.tmp_root, zipname)

        def _radius2bbox(lng, lat, radius):
            return (lng - radius, lat - radius,
                    lng + radius, lat + radius)

        self.mkdirs(trek_file)

        def close_zip(zipfile):
            return self.close_zip(zipfile, zipname)

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

    def sync_global_tiles(self):
        """ Creates a tiles file on the global extent.
        """
        zipname = os.path.join('mobile', 'tiles', 'global.zip')

        if self.verbosity == 2:
            self.stdout.write(u"\x1b[36m**\x1b[0m \x1b[1m{name}\x1b[0m ...".format(name=zipname), ending="")
            self.stdout.flush()

        global_extent = settings.LEAFLET_CONFIG['SPATIAL_EXTENT']

        logger.info("Global extent is %s" % unicode(global_extent))
        global_file = os.path.join(self.tmp_root, zipname)

        logger.info("Build global tiles file...")
        self.mkdirs(global_file)

        def close_zip(zipfile):
            return self.close_zip(zipfile, zipname)

        tiles = ZipTilesBuilder(global_file, close_zip, **self.builder_args)
        tiles.add_coverage(bbox=global_extent,
                           zoomlevels=settings.MOBILE_TILES_GLOBAL_ZOOMS)
        tiles.run()

    def sync_tiles(self):
        if not self.skip_tiles:

            if self.celery_task:
                self.celery_task.update_state(
                    state='PROGRESS',
                    meta={
                        'name': self.celery_task.name,
                        'current': 10,
                        'total': 100,
                        'infos': u"{}".format(_(u"Global tiles syncing ..."))
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
                        'infos': u"{}".format(_(u"Trek tiles syncing ..."))
                    }
                )

            treks = trekking_models.Trek.objects.existing().order_by('pk')

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
                        'infos': u"{}".format(_(u"Tiles synced ..."))
                    }
                )

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
                        'infos': u"{} : {} ...".format(_(u"Language"), lang)
                    }
                )
                current_value = current_value + step_value

            translation.activate(lang)
            self.sync_trekking(lang)
            if 'geotrek.flatpages' in settings.INSTALLED_APPS:
                self.sync_flatpage(lang)
            translation.deactivate()

    def check_dst_root_is_empty(self):
        if not os.path.exists(self.dst_root):
            return
        existing = set([os.path.basename(p) for p in os.listdir(self.dst_root)])
        remaining = existing - set(('api', 'media', 'meta', 'static', 'zip', 'mobile'))
        if remaining:
            raise CommandError(u"Destination directory contains extra data")

    def rename_root(self):
        if os.path.exists(self.dst_root):
            tmp_root2 = os.path.join(os.path.dirname(self.dst_root), 'deprecated_sync_mobile')
            os.rename(self.dst_root, tmp_root2)
            os.rename(self.tmp_root, self.dst_root)
            shutil.rmtree(tmp_root2)
        else:
            os.rename(self.tmp_root, self.dst_root)

    def handle(self, *args, **options):
        self.successfull = True
        self.verbosity = options['verbosity']
        self.skip_tiles = options['skip_tiles']
        self.factory = RequestFactory()
        self.dst_root = options["path"].rstrip('/')
        self.abs_path = os.path.abspath(options["path"])
        self.check_dst_root_is_empty()
        self.tmp_root = os.path.join(os.path.dirname(self.dst_root), 'tmp_sync_mobile')
        os.mkdir(self.tmp_root)
        if options['languages']:
            self.languages = options['languages'].split(',')
        else:
            self.languages = settings.MODELTRANSLATION_LANGUAGES
        self.celery_task = options.get('task', None)

        if options['portal'] is not None:
            self.portal = options['portal'].split(',')
        else:
            self.portal = []

        if options['url'][:7] not in ('http://', 'https://'):
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
            'tiles_dir': os.path.join(settings.DEPLOY_ROOT, 'var', 'tiles'),
        }

        try:
            self.sync()
        except Exception:
            shutil.rmtree(self.tmp_root)
            raise

        self.rename_root()
        shutil.rmtree("{path}/media".format(path=self.abs_path))

        done_message = 'Done'
        if self.successfull:
            done_message = self.style.SUCCESS(done_message)

        if self.verbosity >= 1:
            self.stdout.write(done_message)

        if not self.successfull:
            raise CommandError('Some errors raised during synchronization.')

        sleep(2)  # end sleep to ensure sync page get result
