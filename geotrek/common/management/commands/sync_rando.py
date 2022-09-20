import argparse
import logging
import filecmp
import os
import stat
import shutil
import tempfile
from time import sleep
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.test.client import RequestFactory
from django.utils import translation
from django.utils.translation import gettext as _

from geotrek.common.models import FileType  # NOQA
from geotrek.altimetry.views import ElevationProfile, ElevationArea, serve_elevation_chart
from geotrek.common import models as common_models

from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models

from geotrek.common import helpers_sync as common_sync
from geotrek.trekking import helpers_sync as trekking_sync

if 'geotrek.diving' in settings.INSTALLED_APPS:
    from geotrek.diving import helpers_sync as diving_sync
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from geotrek.sensitivity import helpers_sync as sensitivity_sync
if 'geotrek.signage' in settings.INSTALLED_APPS:
    from geotrek.signage import helpers_sync as signage_sync
if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
    from geotrek.infrastructure import helpers_sync as infrastructure_sync
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    from geotrek.flatpages import helpers_sync as flatpage_sync
if 'geotrek.feedback' in settings.INSTALLED_APPS:
    from geotrek.feedback import helpers_sync as feedback_sync
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import helpers_sync as tourism_sync
# Register mapentity models
from geotrek.trekking import urls  # NOQA
from geotrek.tourism import urls  # NOQA


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('--empty-tmp-folder', dest='empty_tmp_folder', action='store_true', default=False,
                            help='Empty tmp folder')
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

    def get_params_portal(self, params):
        if self.portal:
            params['portal'] = self.portal

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
        tiles = common_sync.ZipTilesBuilder(zipfile, **self.builder_args)
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
        tiles = common_sync.ZipTilesBuilder(zipfile, **self.builder_args)

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
        self.get_params_portal(params)
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, fix2028=True, **kwargs)

    def sync_geojson(self, lang, viewset, name, zipfile=None, params={}, **kwargs):
        view = viewset.as_view({'get': 'list'})
        name = os.path.join('api', lang, name)
        params = params.copy()
        params.update({'format': 'geojson'})

        if self.source:
            params['source'] = ','.join(self.source)

        self.get_params_portal(params)

        self.sync_view(lang, view, name, params=params, zipfile=zipfile, fix2028=True, **kwargs)

    def sync_object_view(self, lang, obj, view, basename_fmt, zipfile=None, params={}, **kwargs):
        translation.activate(lang)
        modelname = obj._meta.model_name
        name = os.path.join('api', lang, '{modelname}s'.format(modelname=modelname), str(obj.pk),
                            basename_fmt.format(obj=obj))
        self.sync_view(lang, view, name, params=params, zipfile=zipfile, pk=obj.pk, **kwargs)
        translation.deactivate()

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

    def sync_metas(self, lang, metaview, obj=None):
        params = {'rando_url': self.rando_url, 'lang': lang}
        self.get_params_portal(params)
        if obj:
            name = os.path.join('meta', lang, obj.rando_url, 'index.html')
            self.sync_view(lang, metaview.as_view(), name, pk=obj.pk, params=params)
        else:
            name = os.path.join('meta', lang, 'index.html')
            self.sync_view(lang, metaview.as_view(), name, params=params)

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

    def sync_pictograms(self, lang, models, zipfile=None):
        for model in models:
            for obj in model.objects.all():
                self.sync_media_file(lang, obj.pictogram, zipfile=zipfile)

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
                treks = treks.filter(Q(portal__name=self.portal) | Q(portal=None))

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
            dst = os.path.join(self.tmp_root, 'api', lang, '{modelname}s'.format(modelname=modelname), str(obj.pk),
                               obj.slug + '.pdf')
            self.mkdirs(dst)
            os.link(src, dst)
            if self.verbosity == 2:
                self.stdout.write("\x1b[36m{lang}\x1b[0m \x1b[1m{dst}\x1b[0m \x1b[32mcopied\x1b[0m".format(lang=lang,
                                                                                                           dst=dst))
        elif settings.ONLY_EXTERNAL_PUBLIC_PDF:
            return
        else:
            params = {}
            if self.source:
                params['source'] = self.source[0]
            self.get_params_portal(params)
            self.sync_object_view(lang, obj, view, '{obj.slug}.pdf', params=params, slug=obj.slug)

    def sync(self):
        step_value = int(50 / len(settings.MODELTRANSLATION_LANGUAGES))
        current_value = 30
        self.sync_tiles()
        subcommands = [trekking_sync.SyncRando(self), common_sync.SyncRando(self)]
        if self.with_signages and 'geotrek.signage' in settings.INSTALLED_APPS:
            subcommands.append(signage_sync.SyncRando(self))
        if self.with_infrastructures and 'geotrek.infrastructure' in settings.INSTALLED_APPS:
            subcommands.append(infrastructure_sync.SyncRando(self))
        if 'geotrek.flatpages' in settings.INSTALLED_APPS:
            subcommands.append(flatpage_sync.SyncRando(self))
        if 'geotrek.feedback' in settings.INSTALLED_APPS:
            subcommands.append(feedback_sync.SyncRando(self))
        if self.with_dives and 'geotrek.diving' in settings.INSTALLED_APPS:
            subcommands.append(diving_sync.SyncRando(self))
        if 'geotrek.tourism' in settings.INSTALLED_APPS:
            subcommands.append(tourism_sync.SyncRando(self))
        if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
            subcommands.append(sensitivity_sync.SyncRando(self))
        for subcommand in subcommands:
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

                zipname = os.path.join('zip', 'treks', lang, 'global.zip')
                zipfullname = os.path.join(self.tmp_root, zipname)
                self.mkdirs(zipfullname)
                self.zipfile = ZipFile(zipfullname, 'w')

                translation.activate(lang)
                subcommand.sync(lang)
                translation.deactivate()

                if self.verbosity == 2:
                    self.stdout.write("{lang} {name} ...".format(lang=lang, name=zipname), ending="")

                self.close_zip(self.zipfile, zipname)

        self.sync_static_file('**', 'tourism/touristicevent.svg')
        self.sync_pictograms('**', [tourism_models.InformationDeskType, tourism_models.TouristicContentCategory,
                                    tourism_models.TouristicContentType, tourism_models.TouristicEventType])

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
            shutil.rmtree(tmp_root2)
        os.rename(self.tmp_root, self.dst_root)
        os.chmod(self.dst_root, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
        os.mkdir(self.tmp_root)  # Recreate otherwise python3.6 will complain it does not find the tmp dir at cleanup.

    def handle(self, *args, **options):
        self.options = options
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

        self.portal = options['portal']
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
        sync_rando_tmp_dir = os.path.join(settings.TMP_DIR, 'sync_rando')
        if options['empty_tmp_folder']:
            for dir in os.listdir(sync_rando_tmp_dir):
                shutil.rmtree(os.path.join(sync_rando_tmp_dir, dir))
        if not os.path.exists(settings.TMP_DIR):
            os.mkdir(settings.TMP_DIR)
        if not os.path.exists(sync_rando_tmp_dir):
            os.mkdir(sync_rando_tmp_dir)
        with tempfile.TemporaryDirectory(dir=sync_rando_tmp_dir) as tmp_dir:
            self.tmp_root = tmp_dir
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
            self.rename_root()

        done_message = 'Done'
        if self.successfull:
            done_message = self.style.SUCCESS(done_message)

        if self.verbosity >= 1:
            self.stdout.write(done_message)

        if not self.successfull:
            raise CommandError('Some errors raised during synchronization.')

        sleep(2)  # end sleep to ensure sync page get result
