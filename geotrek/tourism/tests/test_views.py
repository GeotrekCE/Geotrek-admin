import hashlib
import json
import os
from datetime import datetime
from shutil import rmtree
from tempfile import mkdtemp
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group, Permission

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from embed_video.backends import detect_backend
from paperclip.models import random_suffix_regexp

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import (StructureFactory, UserFactory,
                                             UserProfileFactory)
from geotrek.common.models import Attachment, FileType
from geotrek.common.tests import TranslationResetMixin
from geotrek.common.tests import factories as common_factories
from geotrek.common.utils.testdata import (get_dummy_uploaded_document,
                                           get_dummy_uploaded_image)
from geotrek.core.tests import factories as core_factories
from geotrek.tourism.tests.factories import (InformationDeskFactory,
                                             TouristicContentCategoryFactory,
                                             TouristicContentFactory,
                                             TouristicContentType1Factory,
                                             TouristicContentType2Factory,
                                             TouristicEventFactory)
from geotrek.tourism.filters import TouristicContentFilterSet, TouristicEventFilterSet
from geotrek.trekking.tests import factories as trekking_factories
from geotrek.trekking.tests.base import TrekkingManagerTest
from geotrek.zoning.tests import factories as zoning_factories

PNG_BLACK_PIXEL = bytes.fromhex(
    '89504e470d0a1a0a0000000d4948445200000001000000010804000000b51c0c0200'
    '00000b4944415478da6364f80f00010501012718e3660000000049454e44ae426082'
)


class TouristicContentViewsSameStructureTests(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        cls.user = profile.user
        cls.user.groups.add(Group.objects.get(name="Référents communication"))
        cls.content1 = TouristicContentFactory.create()
        structure = StructureFactory.create()
        cls.content2 = TouristicContentFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(user=self.user)

    def tearDown(self):
        self.client.logout()

    def test_can_edit_same_structure(self):
        url = "/touristiccontent/edit/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = "/touristiccontent/edit/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/touristiccontent/{pk}/".format(pk=self.content2.pk))

    def test_can_delete_same_structure(self):
        url = "/touristiccontent/delete/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = "/touristiccontent/delete/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/touristiccontent/{pk}/".format(pk=self.content2.pk))

    def test_contents_on_treks_do_not_exist(self):
        response = self.client.get('api/en/treks/0/touristiccontents.geojson')
        self.assertEqual(response.status_code, 404)

    def test_contents_on_treks_not_public(self):
        trek = trekking_factories.TrekFactory.create(published=False)
        response = self.client.get('api/en/treks/{}/touristiccontents.geojson'.format(trek.pk))
        self.assertEqual(response.status_code, 404)


class TouristicContentTemplatesTest(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = TouristicContentFactory.create()
        cat = cls.content.category
        cat.type1_label = 'Michelin'
        cat.save()
        cls.category2 = TouristicContentCategoryFactory(label="Another category")

    def setUp(self):
        self.login()

    def tearDown(self):
        self.client.logout()

    def test_only_used_categories_are_shown(self):
        url = "/touristiccontent/list/"
        response = self.client.get(url)
        self.assertContains(response, 'title="Category"')
        self.assertNotContains(response, 'title="Another category"')

    def test_shown_in_details_when_enabled(self):
        url = "/touristiccontent/%s/" % self.content.pk
        response = self.client.get(url)
        self.assertContains(response, 'Tourism')

    @override_settings(TOURISM_ENABLED=False)
    def test_not_tourism_detail_fragment_displayed(self):
        """Test in other module, if tourism_detail_fragment.html is not displayed."""
        trek = trekking_factories.TrekFactory.create()
        url = "/trek/%s/" % trek.pk
        response = self.client.get(url)
        self.assertNotContains(response, 'Tourism')

    def test_type_label_shown_in_detail_page(self):
        url = "/touristiccontent/{pk}/".format(pk=self.content.pk)
        response = self.client.get(url)
        self.assertContains(response, 'Michelin')


class TouristicContentFormTest(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = TouristicContentCategoryFactory()

    def setUp(self):
        self.login()

    def test_no_category_selected_by_default(self):
        url = "/touristiccontent/add/"
        response = self.client.get(url)
        self.assertNotContains(response, 'value="%s" selected' % self.category.pk)

    def test_default_category_is_taken_from_url_params(self):
        url = "/touristiccontent/add/?category=%s" % self.category.pk
        response = self.client.get(url)
        self.assertContains(response, 'value="%s" selected' % self.category.pk)


class BasicJSONAPITest(TranslationResetMixin):
    factory = None

    @classmethod
    def setUpTestData(cls):
        polygon = 'SRID=%s;MULTIPOLYGON(((0 0, 0 3, 3 3, 3 0, 0 0)))' % settings.SRID
        cls.city = zoning_factories.CityFactory(geom=polygon)
        cls.district = zoning_factories.DistrictFactory(geom=polygon)
        cls.portal = common_factories.TargetPortalFactory()
        cls.theme = common_factories.ThemeFactory()

        cls.content = cls.factory(geom='SRID=%s;POINT(1 1)' % settings.SRID,
                                  portals=[cls.portal], themes=[cls.theme])

        cls.picture = common_factories.AttachmentFactory(content_object=cls.content,
                                                         attachment_file=get_dummy_uploaded_image())
        cls.document = common_factories.AttachmentFactory(content_object=cls.content,
                                                          attachment_file=get_dummy_uploaded_document())

        cls.content.themes.add(cls.theme)
        cls.source = common_factories.RecordSourceFactory()
        cls.content.source.add(cls.source)

        cls.content.portal.add(cls.portal)
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = core_factories.PathFactory(geom='SRID=%s;LINESTRING(0 10, 10 10)' % settings.SRID)
            cls.trek = trekking_factories.TrekFactory(paths=[path])
            cls.poi = trekking_factories.POIFactory(paths=[(path, 0.5, 0.5)])
        else:
            cls.trek = trekking_factories.TrekFactory(geom='SRID=%s;LINESTRING(0 10, 10 10)' % settings.SRID)
            cls.poi = trekking_factories.POIFactory(geom='SRID=%s;POINT(0 5)' % settings.SRID)

    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT="{title} {author}")
    def setUp(self):
        super().setUp()
        self.pk = self.content.pk
        url = '/api/en/{model}s/{pk}.json'.format(model=self.content._meta.model_name, pk=self.pk)
        self.response = self.client.get(url)
        self.result = self.response.json()

    def test_thumbnail(self):
        self.assertEqual(self.result['thumbnail'],
                         self.picture.attachment_file.url + '.120x120_q85_crop.png')

    def test_published_status(self):
        self.assertDictEqual(self.result['published_status'][0],
                             {'lang': 'en', 'status': True, 'language': 'English'})

    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT="{title} {author}")
    def test_pictures(self):
        url = '{url}.800x800_q85_watermark-{id}.png'.format(
            url=self.picture.attachment_file.url,
            id=hashlib.md5(
                settings.THUMBNAIL_COPYRIGHT_FORMAT.format(
                    author=self.picture.author,
                    title=self.picture.title,
                    legend=self.picture.legend).encode()).hexdigest())
        raise Exception(self.result)
        self.assertDictEqual(self.result['pictures'][0],
                             {'url': url,
                              'title': self.picture.title,
                              'legend': self.picture.legend,
                              'author': self.picture.author})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_files(self):
        self.assertDictEqual(self.result['files'][0],
                             {'url': os.path.join(settings.MEDIA_URL, self.document.attachment_file.name),
                              'title': self.document.title,
                              'legend': self.document.legend,
                              'author': self.document.author})

    def test_video_youtube(self):
        video_youtube = common_factories.AttachmentFactory(content_object=self.content, attachment_file='',
                                                           attachment_video='https://www.youtube.com/embed/Jm3anSjly0Y?wmode=opaque')
        video_detected_youtube = detect_backend(video_youtube.attachment_video)
        pk = self.content.pk
        url = '/api/en/{model}s/{pk}.json'.format(model=self.content._meta.model_name, pk=pk)
        response = self.client.get(url)
        result = response.json()
        self.assertDictEqual(result['videos'][0],
                             {'backend': 'Youtube',
                              'url': 'https://www.youtube.com/embed/Jm3anSjly0Y?wmode=opaque',
                              'title': video_youtube.title,
                              'legend': video_youtube.legend,
                              'author': video_youtube.author,
                              'code': video_detected_youtube.code})

    def test_video_dailymotion(self):
        video_dailymotion = common_factories.AttachmentFactory(
            content_object=self.content, attachment_file='',
            attachment_video='https://www.dailymotion.com/video/x6e0q24')
        video_detected_dailymotion = detect_backend(video_dailymotion.attachment_video)
        pk = self.content.pk
        url = '/api/en/{model}s/{pk}.json'.format(model=self.content._meta.model_name, pk=pk)
        response = self.client.get(url)
        result = response.json()

        self.assertDictEqual(result['videos'][0],
                             {'backend': 'Dailymotion',
                              'url': 'https://www.dailymotion.com/embed/video/x6e0q24',
                              'title': video_dailymotion.title,
                              'legend': video_dailymotion.legend,
                              'author': video_dailymotion.author,
                              'code': video_detected_dailymotion.code})

    def test_video_dailymotion_wrong_id(self):
        common_factories.AttachmentFactory(
            content_object=self.content, attachment_file='',
            attachment_video='https://www.dailymotion.com/video/noid')

        pk = self.content.pk
        url = '/api/en/{model}s/{pk}.json'.format(model=self.content._meta.model_name, pk=pk)
        response = self.client.get(url)
        result = json.loads(response.content.decode())
        self.assertFalse(result['videos'])

    def test_cities(self):
        self.assertDictEqual(self.result['cities'][0],
                             {"code": self.city.code,
                              "name": self.city.name})

    def test_districts(self):
        self.assertDictEqual(self.result['districts'][0],
                             {"id": self.district.id,
                              "name": self.district.name})

    def test_themes(self):
        self.assertDictEqual(self.result['themes'][0],
                             {"id": self.theme.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.theme.pictogram.name),
                              "label": self.theme.label})

    def test_treks(self):
        self.assertDictEqual(self.result['treks'][0], {
            'id': self.trek.id,
            'category_id': 'T'})

    def test_pois(self):
        self.assertDictEqual(self.result['pois'][0], {
            'id': self.poi.id,
            'slug': self.poi.slug,
            'name': self.poi.name,
            'type': {
                'id': self.poi.type.id,
                'label': self.poi.type.label,
                'pictogram': os.path.join(settings.MEDIA_URL, self.poi.type.pictogram.name)}})

    def test_sources(self):
        self.assertDictEqual(self.result['source'][0], {
            'name': self.source.name,
            'website': self.source.website,
            "pictogram": os.path.join(settings.MEDIA_URL, self.source.pictogram.name)})

    def test_portals(self):
        '''
        Test if portal correctly serialized
        '''
        self.assertDictEqual(
            self.result['portal'][0],
            {'name': self.portal.name,
             'website': self.portal.website, })

    def test_approved(self):
        self.assertFalse(self.result['approved'])


class TouristicContentAPITest(BasicJSONAPITest, TrekkingManagerTest):
    factory = TouristicContentFactory

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = cls.content.category
        cls.type1 = TouristicContentType1Factory(category=cls.category)
        cls.type2 = TouristicContentType2Factory(category=cls.category, pictogram=None)
        cls.content.type1.set([cls.type1])
        cls.content.type2.set([cls.type2])

    def test_expected_properties(self):
        self.assertEqual(sorted([
            'accessibility', 'approved', 'areas', 'category', 'cities', 'contact',
            'description', 'description_teaser', 'districts', 'email',
            'filelist_url', 'files', 'id', 'label_accessibility', 'map_image_url', 'name', 'pictures',
            'pois', 'practical_info', 'printable', 'publication_date',
            'published', 'published_status', 'reservation_id', 'reservation_system',
            'slug', 'source', 'structure', 'portal', 'themes', 'thumbnail', 'touristic_contents',
            'touristic_events', 'treks', 'type1', 'type2', 'videos', 'website', 'dives']),
            sorted(self.result.keys()))

    def test_type1(self):
        self.assertDictEqual(self.result['type1'][0],
                             {"id": self.type1.id,
                              "name": self.type1.label,
                              'pictogram': os.path.join(settings.MEDIA_URL, self.type1.pictogram.name),
                              "in_list": self.type1.in_list})

    def test_type2(self):
        self.assertDictEqual(self.result['type2'][0],
                             {"id": self.type2.id,
                              "name": self.type2.label,
                              'pictogram': None,
                              "in_list": self.type2.in_list})

    def test_category(self):
        self.assertDictEqual(self.result['category'], {
            "id": self.category.prefixed_id,
            "order": None,
            "label": self.category.label,
            "slug": "touristic-content",
            "type1_label": self.content.type1_label,
            "type2_label": self.content.type2_label,
            "pictogram": os.path.join(settings.MEDIA_URL, self.category.pictogram.name)})


class TouristicEventAPITest(BasicJSONAPITest, TrekkingManagerTest):
    factory = TouristicEventFactory

    def test_expected_properties(self):
        self.assertEqual(sorted([
            'accessibility', 'approved', 'areas', 'begin_date', 'booking', 'category',
            'cities', 'contact', 'description', 'description_teaser',
            'districts', 'duration', 'email', 'end_date', 'filelist_url', 'files',
            'id', 'map_image_url', 'meeting_point', 'start_time', 'end_time', 'name',
            'organizers', 'capacity', 'pictures', 'pois', 'portal', 'practical_info',
            'printable', 'publication_date', 'published', 'published_status',
            'slug', 'source', 'speaker', 'structure', 'target_audience', 'themes',
            'thumbnail', 'touristic_contents', 'touristic_events', 'treks', 'type',
            'type1', 'videos', 'website', 'dives']),
            sorted(self.result.keys()))

    def test_type(self):
        self.assertDictEqual(self.result['type'],
                             {"id": self.content.type.id,
                              'pictogram': os.path.join(settings.MEDIA_URL, self.content.type.pictogram.name),
                              "name": self.content.type.type})

    def test_type1(self):
        self.assertDictEqual(self.result['type1'][0],
                             {"id": self.content.type.id,
                              'pictogram': os.path.join(settings.MEDIA_URL, self.content.type.pictogram.name),
                              "name": self.content.type.type})

    def test_category(self):
        self.assertDictEqual(self.result['category'],
                             {"id": 'E',
                              "order": 99,
                              "label": "Touristic events",
                              "slug": "touristic-event",
                              "type1_label": "Type",
                              "pictogram": "/static/tourism/touristicevent.svg"})


class TouristicEventViewsSameStructureTests(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        cls.user = profile.user
        cls.user.groups.add(Group.objects.get(name="Référents communication"))

        cls.event1 = TouristicEventFactory.create()
        structure = StructureFactory.create()
        cls.event2 = TouristicEventFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_can_edit_same_structure(self):
        url = "/touristicevent/edit/{pk}/".format(pk=self.event1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = "/touristicevent/edit/{pk}/".format(pk=self.event2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/touristicevent/{pk}/".format(pk=self.event2.pk))

    def test_can_delete_same_structure(self):
        url = "/touristicevent/delete/{pk}/".format(pk=self.event1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = "/touristicevent/delete/{pk}/".format(pk=self.event2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/touristicevent/{pk}/".format(pk=self.event2.pk))

    def test_events_on_treks_do_not_exist(self):
        response = self.client.get('/api/en/treks/0/touristicevents.geojson')
        self.assertEqual(response.status_code, 404)

    def test_events_on_treks_not_public(self):
        trek = trekking_factories.TrekFactory.create(published=False)
        response = self.client.get('/api/en/treks/{}/touristicevents.geojson'.format(trek.pk))
        self.assertEqual(response.status_code, 404)


class TouristicContentCustomViewTests(TrekkingManagerTest):

    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        content = TouristicContentFactory.create(published=True)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=mkdtemp('geotrek_test'))
    def test_external_public_document_pdf(self):
        content = TouristicContentFactory.create(published=True)
        Attachment.objects.create(
            filetype=FileType.objects.create(type="Topoguide"),
            content_object=content,
            creator=UserFactory.create(),
            attachment_file=SimpleUploadedFile('external.pdf', b'External PDF')
        )
        rmtree(settings.MEDIA_ROOT)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        regexp = f"/media_secure/paperclip/tourism_touristiccontent/{content.pk}/external{random_suffix_regexp()}.pdf"
        self.assertRegex(response['X-Accel-Redirect'], regexp)

    @override_settings(ONLY_EXTERNAL_PUBLIC_PDF=True)
    def test_only_external_public_document_pdf(self):
        content = TouristicContentFactory.create(published=True)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_published_document_pdf(self):
        content = TouristicContentFactory.create(published=False)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TouristicEventOrganizerCreatePopupTest(TestCase):
    def test_cannot_create_organizer(self):
        url = '/popup/add/organizer/'
        response = self.client.get(url)
        # with no user logged -> redirect to login page
        self.assertRedirects(response, "/login/?next=/popup/add/organizer/")
        user = UserFactory()
        self.client.force_login(user=user)
        response = self.client.get(url)
        # with user with no perm -> redirect to login page
        self.assertEqual(response.status_code, 403)

    def test_can_create_organizer(self):
        user = UserFactory()
        user.user_permissions.add(Permission.objects.get(codename='add_touristiceventorganizer'))
        self.client.force_login(user=user)
        url = '/popup/add/organizer/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data={"label": "test"})
        self.assertIn("dismissAddAnotherPopup", response.content.decode())


class TouristicEventCustomViewTests(TrekkingManagerTest):
    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        content = TouristicEventFactory.create(published=True)
        url = '/api/en/touristicevents/{pk}/slug.pdf'.format(pk=content.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_not_published_document_pdf(self):
        content = TouristicEventFactory.create(published=False)
        url = '/api/en/touristicevents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TouristicEventViewSetTest(TestCase):
    def test_touristic_events_without_enddate_filter(self):
        TouristicEventFactory.create_batch(10, published=True)
        response = self.client.get('/api/en/touristicevents.geojson')
        geojson = response.json()
        self.assertEqual(len(geojson['features']), 10)

    def test_touristic_events_with_enddate_filter(self):
        """
        Relative date: 2020-01-01
        5 events with no end date
        5 events with end date after relative date
        7 events with end date before relative date
                 ->  only events with no end or end in after relative date must be included
        """
        TouristicEventFactory.create_batch(5, end_date=None, published=True)
        TouristicEventFactory.create_batch(5, end_date=datetime.strptime('2020-05-10', '%Y-%m-%d'), published=True)
        TouristicEventFactory.create_batch(7, end_date=datetime.strptime('2010-05-10', '%Y-%m-%d'), published=True)
        response = self.client.get('/api/en/touristicevents.geojson', data={'ends_after': '2020-01-01'})
        geojson = response.json()

        self.assertEqual(len(geojson['features']), 10)


class TouristicCategoryViewTest(TestCase):
    def test_get_categories(self):
        """
        Test category json serialization via api
        """
        nb_elements = 10
        TouristicContentCategoryFactory.create_batch(nb_elements)
        response = self.client.get(reverse('tourism:touristic_categories_json', kwargs={'lang': 'en'}))
        json_response = response.json()
        self.assertEqual(len(json_response), nb_elements)


class InformationDeskAPITest(TestCase):
    def test_geojson(self):
        InformationDeskFactory.create()
        desk2 = InformationDeskFactory.create()
        response = self.client.get('/api/en/information_desks-{}.geojson'.format(desk2.type.id))
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn('features', result)
        self.assertEqual(len(result['features']), 1)
        self.assertEqual(result['features'][0]['type'], 'Feature')
        self.assertEqual(result['features'][0]['geometry']['type'], 'Point')
        self.assertEqual(result['features'][0]['properties']['name'], desk2.name)


class TrekInformationDeskAPITest(TestCase):
    def test_geojson(self):
        trek = trekking_factories.TrekFactory()
        desk = InformationDeskFactory.create()
        InformationDeskFactory.create()
        trek.information_desks.add(desk)
        trek.save()
        response = self.client.get('/api/en/treks/{}/information_desks.geojson'.format(trek.pk))
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result['features']), 1)
        self.assertEqual(result['features'][0]['type'], 'Feature')
        self.assertEqual(result['features'][0]['geometry']['type'], 'Point')
        self.assertEqual(result['features'][0]['properties']['name'], desk.name)


class TouristicContentFilterTest(TestCase):
    factory = TouristicContentFactory
    filterset = TouristicContentFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = TouristicContentFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        touristic_content1 = TouristicContentFactory.create(provider='my_provider1')
        touristic_content2 = TouristicContentFactory.create(provider='my_provider2')

        filter_set = TouristicContentFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(touristic_content1, filter_set.qs)
        self.assertIn(touristic_content2, filter_set.qs)


class TouristicEventFilterTest(TestCase):
    factory = TouristicEventFactory
    filterset = TouristicEventFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = TouristicEventFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        touristic_event1 = TouristicEventFactory.create(provider='my_provider1')
        touristic_event2 = TouristicEventFactory.create(provider='my_provider2')

        filter_set = TouristicEventFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(touristic_event1, filter_set.qs)
        self.assertIn(touristic_event2, filter_set.qs)
