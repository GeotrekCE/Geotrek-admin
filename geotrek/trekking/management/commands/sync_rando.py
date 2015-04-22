from optparse import make_option
import os
import shutil

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
        fullname = os.path.join(self.dst_root, name)
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
        self.stdout.write(fullname)

    def sync_geojson(self, lang, viewset, name):
        view = viewset.as_view({'get': 'list'})
        name = os.path.join('api', lang, '{name}.geojson'.format(name=name))
        self.sync_view(lang, view, name)

    def sync_pois(self, lang):
        view = POIViewSet.as_view({'get': 'list'})
        for trek in trekking_models.Trek.objects.filter(**{'published_{lang}'.format(lang=lang): True}):
            name = os.path.join('api', lang, 'treks', str(trek.pk), 'pois.geojson')
            self.sync_view(lang, view, name, pk=trek.pk)

    def sync_exports(self, lang, model, view, ext):
        for obj in model.objects.filter(**{'published_{lang}'.format(lang=lang): True}):
            modelname = model._meta.model_name
            name = os.path.join('api', lang, '{modelname}s'.format(modelname=modelname), str(obj.pk), '{slug}.{ext}'.format(slug=obj.slug, ext=ext))
            self.sync_view(lang, view, name, pk=obj.pk)

    def sync_pdfs(self, lang, model):
        self.sync_exports(lang, model, DocumentPublicPDF.as_view(model=model), 'pdf')

    def sync_profiles(self, treks):
        view = ElevationProfile.as_view(model=trekking_models.Trek)
        for trek in treks:
            name = os.path.join('api', 'treks', str(trek.pk), 'profile.json')
            self.sync_view('en', view, name, pk=trek.pk)

    def sync_dems(self, treks):
        view = ElevationArea.as_view(model=trekking_models.Trek)
        for trek in treks:
            name = os.path.join('api', 'treks', str(trek.pk), 'dem.json')
            self.sync_view('en', view, name, pk=trek.pk)

    def sync_file(self, name, src_root, url):
        url = url.strip('/')
        src = os.path.join(src_root, name)
        dst = os.path.join(self.dst_root, url, name)
        self.mkdirs(dst)
        shutil.copyfile(src, dst)
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

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError(u"Missing parameter destination directory")
        self.dst_root = args[0]
        if(options['url'][:7] != 'http://'):
            raise CommandError('url parameter should start with http://')
        self.rooturl = options['url'][7:]

        self.factory = RequestFactory()
        self.languages = [lang for lang, name in settings.LANGUAGES]

        for lang in self.languages:
            self.sync_geojson(lang, TrekViewSet, 'treks')
            self.sync_geojson(lang, FlatPageViewSet, 'flatpages')
            self.sync_pois(lang)
            self.sync_exports(lang, trekking_models.Trek, TrekGPXDetail.as_view(), 'gpx')
            self.sync_exports(lang, trekking_models.Trek, TrekKMLDetail.as_view(), 'kml')
            self.sync_pdfs(lang, trekking_models.Trek)

        treks = trekking_models.Trek.objects.filter(self.any_published_q())
        self.sync_profiles(treks)
        self.sync_dems(treks)

        self.sync_static_file('trekking/trek.svg')

        self.sync_pictograms(common_models.Theme)
        self.sync_pictograms(trekking_models.TrekNetwork)
        self.sync_pictograms(trekking_models.Practice)
        self.sync_pictograms(trekking_models.Accessibility)
        self.sync_pictograms(trekking_models.Route)
        self.sync_pictograms(trekking_models.DifficultyLevel)
        self.sync_pictograms(trekking_models.WebLinkCategory)
        self.sync_pictograms(trekking_models.POIType)

        self.sync_attachments(trekking_models.Trek)
        self.sync_attachments(trekking_models.POI)
