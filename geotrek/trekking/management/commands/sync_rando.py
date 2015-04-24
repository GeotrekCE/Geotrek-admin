from optparse import make_option
import os
import shutil
import tempfile

from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.management.base import BaseCommand, CommandError
from django.test.client import RequestFactory
from django.utils import translation

# Workaround https://code.djangoproject.com/ticket/22865
from geotrek.common.models import FileType  # NOQA

from geotrek.altimetry.views import ElevationProfile, ElevationArea
from geotrek.common import models as common_models
from geotrek.trekking import models as trekking_models
from geotrek.common.views import DocumentPublicPDF
from geotrek.trekking.views import TrekViewSet, POIViewSet, TrekGPXDetail, TrekKMLDetail
from geotrek.flatpages.views import FlatPageViewSet


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--url', '-u', action='store', dest='url',
                    default='http://localhost',
                    help='Base url'),
    )

    def mkdirs(self, name):
        dirname = os.path.dirname(name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def sync_view(self, lang, view, name, **kwargs):
        fullname = os.path.join(self.tmp_root, name)
        self.mkdirs(fullname)
        request = self.factory.get('', HTTP_HOST=self.rooturl)
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
        if self.verbosity == '2':
            self.stdout.write(fullname)

    def sync_geojson(self, lang, viewset, name):
        if self.verbosity >= '1':
            self.stdout.write("Sync {lang} {name} GeoJSON".format(lang=lang, name=name))
        view = viewset.as_view({'get': 'list'})
        name = os.path.join('api', lang, '{name}.geojson'.format(name=name))
        self.sync_view(lang, view, name)

    def sync_pois(self, lang):
        if self.verbosity >= '1':
            self.stdout.write("Sync {lang} POI".format(lang=lang))
        view = POIViewSet.as_view({'get': 'list'})
        for trek in trekking_models.Trek.objects.filter(**{'published_{lang}'.format(lang=lang): True}):
            name = os.path.join('api', lang, 'treks', str(trek.pk), 'pois.geojson')
            self.sync_view(lang, view, name, pk=trek.pk)

    def sync_object_view(self, lang, model, view, basename_fmt):
        for obj in model.objects.filter(**{'published_{lang}'.format(lang=lang): True}):
            modelname = model._meta.model_name
            name = os.path.join('api', lang, '{modelname}s'.format(modelname=modelname), str(obj.pk), basename_fmt.format(obj=obj))
            self.sync_view(lang, view, name, pk=obj.pk)

    def sync_pdfs(self, lang, model):
        if self.verbosity >= '1':
            self.stdout.write("Sync {lang} PDF".format(lang=lang))
        view = DocumentPublicPDF.as_view(model=model)
        self.sync_object_view(lang, model, view, '{obj.slug}.pdf')

    def sync_profiles(self, lang, model):
        if self.verbosity >= '1':
            self.stdout.write("Sync {lang} altimetry profile".format(lang=lang))
        view = ElevationProfile.as_view(model=trekking_models.Trek)
        self.sync_object_view(lang, model, view, 'profile.json')

    def sync_dems(self, lang, model):
        if self.verbosity >= '1':
            self.stdout.write("Sync {lang} DEM".format(lang=lang))
        view = ElevationArea.as_view(model=trekking_models.Trek)
        self.sync_object_view(lang, model, view, 'dem.json')

    def sync_trek_gpx(self, lang):
        if self.verbosity >= '1':
            self.stdout.write("Sync {lang} GPX".format(lang=lang))
        self.sync_object_view(lang, trekking_models.Trek, TrekGPXDetail.as_view(), '{obj.slug}.gpx')

    def sync_trek_kml(self, lang):
        if self.verbosity >= '1':
            self.stdout.write("Sync {lang} KML".format(lang=lang))
        self.sync_object_view(lang, trekking_models.Trek, TrekKMLDetail.as_view(), '{obj.slug}.kml')

    def sync_file(self, name, src_root, url):
        url = url.strip('/')
        src = os.path.join(src_root, name)
        dst = os.path.join(self.tmp_root, url, name)
        self.mkdirs(dst)
        shutil.copyfile(src, dst)
        if self.verbosity == '2':
            self.stdout.write(dst)

    def sync_static_file(self, name):
        self.sync_file(name, settings.STATIC_ROOT, settings.STATIC_URL)

    def sync_media_file(self, field):
        self.sync_file(field.name, settings.MEDIA_ROOT, settings.MEDIA_URL)

    def sync_pictograms(self, model):
        for obj in model.objects.exclude(pictogram=''):
            self.sync_media_file(obj.pictogram)

    def any_published_q(self):
        if self.languages == ['']:
            return Q(published=True)
        q = Q()
        for lang in self.languages:
            q |= Q(**{'published_{lang}'.format(lang=lang): True})
        return q

    def sync_attachments(self, model):
        for obj in model.objects.filter(self.any_published_q()):
            thumbnail = obj.thumbnail
            if thumbnail:
                self.sync_media_file(thumbnail)
            for picture, thdetail in obj.resized_pictures:
                self.sync_media_file(thdetail)
            for attachment in obj.files:
                self.sync_media_file(attachment.attachment_file)

    def sync(self):
        for lang in self.languages:
            self.sync_geojson(lang, TrekViewSet, 'treks')
            self.sync_geojson(lang, FlatPageViewSet, 'flatpages')
            self.sync_pois(lang)
            self.sync_trek_gpx(lang)
            self.sync_trek_kml(lang)
            self.sync_pdfs(lang, trekking_models.Trek)
            self.sync_profiles(lang, trekking_models.Trek)
            self.sync_dems(lang, trekking_models.Trek)

        if self.verbosity >= '1':
            self.stdout.write("Sync trekking pictograms")

        self.sync_static_file('trekking/trek.svg')
        self.sync_pictograms(common_models.Theme)
        self.sync_pictograms(trekking_models.TrekNetwork)
        self.sync_pictograms(trekking_models.Practice)
        self.sync_pictograms(trekking_models.Accessibility)
        self.sync_pictograms(trekking_models.Route)
        self.sync_pictograms(trekking_models.DifficultyLevel)
        self.sync_pictograms(trekking_models.WebLinkCategory)
        self.sync_pictograms(trekking_models.POIType)

        if self.verbosity >= '1':
            self.stdout.write("Sync trekking attachments")

        self.sync_attachments(trekking_models.Trek)
        self.sync_attachments(trekking_models.POI)

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity', '1')
        if len(args) < 1:
            raise CommandError(u"Missing parameter destination directory")
        dst_root = args[0]
        if os.path.exists(dst_root):
            existing = set([os.path.basename(p) for p in os.listdir(dst_root)])
            remaining = existing - set(('api', 'media', 'static'))
            if remaining:
                raise CommandError(u"Destination directory contains extra data")
        if(options['url'][:7] != 'http://'):
            raise CommandError('url parameter should start with http://')
        self.rooturl = options['url'][7:]
        self.factory = RequestFactory()
        self.languages = [lang for lang, name in settings.LANGUAGES]
        self.tmp_root = tempfile.mkdtemp('_sync_rando', dir=os.path.dirname(dst_root))

        self.sync()

        if os.path.exists(dst_root):
            tmp_root2 = tempfile.mkdtemp('_sync_rando', dir=os.path.dirname(dst_root))
            os.rename(dst_root, os.path.join(tmp_root2, 'to_delete'))
            os.rename(self.tmp_root, dst_root)
            shutil.rmtree(tmp_root2)
        else:
            os.rename(self.tmp_root, dst_root)

        if self.verbosity >= '1':
            self.stdout.write('Done')
