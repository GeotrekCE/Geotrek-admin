# -*- encoding: UTF-8 -

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
from geotrek.feedback.views import CategoryList as FeedbackCategoryList
from geotrek.flatpages.models import FlatPage
from geotrek.infrastructure import models as infrastructure_models
from geotrek.infrastructure.views import InfrastructureViewSet
from geotrek.signage.views import SignageViewSet
from geotrek.tourism import models as tourism_models
from geotrek.tourism import views as tourism_views
from geotrek.trekking import models as trekking_models
from geotrek.api.mobile.views.trekking import (TrekViewSet, POIViewSet)
from geotrek.api.mobile.views.common import FlatPageViewSet, SettingsView
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from geotrek.sensitivity import models as sensitivity_models
    from geotrek.sensitivity import views as sensitivity_views

# Register mapentity models
from geotrek.trekking import urls  # NOQA
from geotrek.tourism import urls  # NOQA


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('--languages', '-l', dest='languages', default='', help='Languages to sync')
        parser.add_argument('--portal', '-P', dest='portal', default=None, help='Filter by portal(s)')

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

        if 'geotrek.flatpages' in settings.INSTALLED_APPS:
            self.sync_json(lang, FlatPageViewSet, 'flatpages', zipfile=self.zipfile_common,
                           as_view_args=[{'get': 'list'}])

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

        for trek in treks:
            self.sync_trek(lang, trek)
            self.sync_geojson(lang, TrekViewSet, 'treks/{pk}.geojson'.format(pk=trek.pk), type_view={'get': 'list'})
        self.sync_common(lang)

        if self.verbosity == 2:
            self.stdout.write(u"\x1b[36m{lang}\x1b[0m \x1b[1m{name}\x1b[0m ...".format(lang=lang, name=zipname_trek),
                              ending="")

        self.close_zip(self.zipfile_trek, zipname_trek)

    def sync(self):
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
