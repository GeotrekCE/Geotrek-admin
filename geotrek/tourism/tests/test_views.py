# -*- coding: utf-8 -*-
import os
import json
import mock
import unittest

from datetime import datetime
from requests.exceptions import ConnectionError
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings
from django.test import TestCase
from django.utils import translation

from geotrek.authent.factories import StructureFactory, UserProfileFactory
from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.trekking.tests import TrekkingManagerTest
from geotrek.core import factories as core_factories
from geotrek.trekking import factories as trekking_factories
from geotrek.zoning import factories as zoning_factories
from geotrek.common import factories as common_factories
from geotrek.common.factories import AttachmentFactory
from geotrek.common.tests import TranslationResetMixin
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_document
from geotrek.tourism.models import DATA_SOURCE_TYPES
from geotrek.tourism.factories import (DataSourceFactory,
                                       InformationDeskFactory,
                                       TouristicContentFactory,
                                       TouristicEventFactory,
                                       TouristicContentCategoryFactory,
                                       TouristicContentTypeFactory)
from embed_video.backends import detect_backend


class TourismAdminViewsTests(TrekkingManagerTest):

    def setUp(self):
        self.source = DataSourceFactory.create()
        self.login()

    def test_trekking_managers_can_access_data_sources_admin_site(self):
        url = reverse('admin:tourism_datasource_changelist')
        response = self.client.get(url)
        self.assertContains(response, 'datasource/%s' % self.source.id)

    def test_datasource_title_is_translated(self):
        url = reverse('admin:tourism_datasource_add')
        response = self.client.get(url)
        self.assertContains(response, 'title_fr')


class DataSourceListViewTests(TrekkingManagerTest):
    def setUp(self):
        self.source = DataSourceFactory.create(title_it='titolo')
        self.login()
        self.url = reverse('tourism:datasource_list_json')
        self.response = self.client.get(self.url)

    def tearDown(self):
        translation.deactivate()
        self.client.logout()

    def test_sources_are_listed_as_json(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/json')

    def test_sources_properties_are_provided(self):
        datasources = json.loads(self.response.content)
        self.assertEqual(len(datasources), 1)
        self.assertEqual(datasources[0]['id'], self.source.id)
        self.assertEqual(datasources[0]['url'], self.source.url)

    def test_sources_respect_request_language(self):
        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='it-IT')
        self.assertEqual(response.status_code, 200)
        datasources = json.loads(response.content)
        self.assertEqual(datasources[0]['title'],
                         self.source.title_it)

    def test_sources_provide_geojson_absolute_url(self):
        datasources = json.loads(self.response.content)
        self.assertEqual(datasources[0]['geojson_url'],
                         u'/api/datasource/datasource-%s.geojson' % self.source.id)


class DataSourceViewTests(TrekkingManagerTest):
    def setUp(self):
        self.source = DataSourceFactory.create(type=DATA_SOURCE_TYPES.GEOJSON)
        self.url = reverse('tourism:datasource_geojson', kwargs={'pk': self.source.pk})
        self.login()

    def tearDown(self):
        self.client.logout()

    def test_source_is_fetched_upon_view_call(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = '{}'
            self.client.get(self.url)
            mocked.assert_called_with(self.source.url)

    def test_empty_source_response_return_empty_data(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = '{}'
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            datasource = json.loads(response.content)
            self.assertEqual(datasource['features'], [])

    def test_source_is_returned_as_geojson_when_invalid_geojson(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = '{"bar": "foo"}'
            response = self.client.get(self.url)
            geojson = json.loads(response.content)
            self.assertEqual(geojson['type'], 'FeatureCollection')
            self.assertEqual(geojson['features'], [])

    def test_source_is_returned_as_geojson_when_invalid_response(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = '404 page not found'
            response = self.client.get(self.url)
            geojson = json.loads(response.content)
            self.assertEqual(geojson['type'], 'FeatureCollection')
            self.assertEqual(geojson['features'], [])

    def test_source_is_returned_as_geojson_when_network_problem(self):
        with mock.patch('requests.get') as mocked:
            mocked.side_effect = ConnectionError
            response = self.client.get(self.url)
            geojson = json.loads(response.content)
            self.assertEqual(geojson['type'], 'FeatureCollection')
            self.assertEqual(geojson['features'], [])


class DataSourceTourInFranceViewTests(TrekkingManagerTest):
    def setUp(self):
        here = os.path.dirname(__file__)
        filename = os.path.join(here, 'data', 'sit-averyon-02.01.14.xml')
        self.sample = open(filename).read()

        self.source = DataSourceFactory.create(type=DATA_SOURCE_TYPES.TOURINFRANCE)
        self.url = reverse('tourism:datasource_geojson', kwargs={'pk': self.source.pk})
        self.login()

    def tearDown(self):
        translation.deactivate()
        self.client.logout()

    def test_source_is_returned_as_geojson_when_tourinfrance(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = "<xml></xml>"
            response = self.client.get(self.url)
            geojson = json.loads(response.content)
            self.assertEqual(geojson['type'], 'FeatureCollection')

    def test_source_is_returned_in_language_request(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = self.sample
            response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='es-ES')
            geojson = json.loads(response.content)
            feature = geojson['features'][0]
            self.assertEqual(feature['properties']['description'],
                             u'Ubicada en la región minera del Aveyron, nuestra casa rural os permitirá decubrir la naturaleza y el patrimonio industrial de la cuenca de Aubin y Decazeville.')


class DataSourceSitraViewTests(TrekkingManagerTest):
    def setUp(self):
        here = os.path.dirname(__file__)
        filename = os.path.join(here, 'data', 'sitra-multilang-10.06.14.json')
        self.sample = open(filename).read()

        self.source = DataSourceFactory.create(type=DATA_SOURCE_TYPES.SITRA)
        self.url = reverse('tourism:datasource_geojson', kwargs={'pk': self.source.pk})
        self.login()

    def tearDown(self):
        translation.deactivate()
        self.client.logout()

    def test_source_is_returned_as_geojson_when_sitra(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = "{}"
            response = self.client.get(self.url)
            geojson = json.loads(response.content)
            self.assertEqual(geojson['type'], 'FeatureCollection')

    def test_source_is_returned_in_language_request(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = self.sample
            response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='es-ES')
            geojson = json.loads(response.content)
            feature = geojson['features'][0]
            self.assertEqual(feature['properties']['title'],
                             u'Refugios en Valgaudemar')

    def test_default_language_is_returned_when_not_available(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = self.sample
            response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='es-ES')
            geojson = json.loads(response.content)
            feature = geojson['features'][0]
            self.assertEqual(feature['properties']['description'],
                             u"Randonnée idéale pour bons marcheurs, une immersion totale dans la vallée du Valgaudemar, au coeur du territoire préservé du Parc national des Ecrins. Un grand voyage ponctué d'étapes en altitude, avec une ambiance chaleureuse dans les refuges du CAF.")

    def test_website_can_be_obtained(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = self.sample
            response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='es-ES')
            geojson = json.loads(response.content)
            feature = geojson['features'][0]
            self.assertEqual(feature['properties']['website'],
                             "http://www.cirkwi.com/#!page=circuit&id=12519&langue=fr")

    def test_phone_can_be_obtained(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = self.sample
            response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='es-ES')
            geojson = json.loads(response.content)
            feature = geojson['features'][0]
            self.assertEqual(feature['properties']['phone'],
                             "04 92 55 23 21")

    def test_geometry_as_geojson(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = self.sample
            response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='es-ES')
            geojson = json.loads(response.content)
            feature = geojson['features'][0]
            self.assertDictEqual(feature['geometry'],
                                 {"type": "Point",
                                  "coordinates": [6.144058, 44.826552]})

    def test_list_of_pictures(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = self.sample
            response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='es-ES')
            geojson = json.loads(response.content)
            feature = geojson['features'][0]
            self.assertDictEqual(feature['properties']['pictures'][0],
                                 {u'copyright': u'Christian Martelet',
                                  u'legend': u'Refuges en Valgaudemar',
                                  u'url': u'http://static.sitra-tourisme.com/filestore/objets-touristiques/images/600938.jpg'})


class TouristicContentViewsSameStructureTests(AuthentFixturesTest):
    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        user = profile.user
        user.groups.add(Group.objects.get(name=u"Référents communication"))
        self.client.login(username=user.username, password='dooh')
        self.content1 = TouristicContentFactory.create()
        structure = StructureFactory.create()
        self.content2 = TouristicContentFactory.create(structure=structure)

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


class TouristicContentTemplatesTest(TrekkingManagerTest):
    def setUp(self):
        self.content = TouristicContentFactory.create()
        cat = self.content.category
        cat.type1_label = 'Michelin'
        cat.save()
        self.category2 = TouristicContentCategoryFactory()
        self.login()

    def tearDown(self):
        self.client.logout()

    def test_only_used_categories_are_shown(self):
        url = "/touristiccontent/list/"
        response = self.client.get(url)
        self.assertContains(response, 'title="%s"' % self.content.category.label)
        self.assertNotContains(response, 'title="%s"' % self.category2.label)

    def test_shown_in_details_when_enabled(self):
        url = "/touristiccontent/%s/" % self.content.pk
        response = self.client.get(url)
        self.assertContains(response, 'Tourism')

    @override_settings(TOURISM_ENABLED=False)
    def test_not_shown_in_details_when_disabled(self):
        url = "/touristiccontent/%s/" % self.content.pk
        response = self.client.get(url)
        self.assertNotContains(response, 'Tourism')

    def test_type_label_shown_in_detail_page(self):
        url = "/touristiccontent/{pk}/".format(pk=self.content.pk)
        response = self.client.get(url)
        self.assertContains(response, 'Michelin')


class TouristicContentFormTest(TrekkingManagerTest):
    def setUp(self):
        self.category = TouristicContentCategoryFactory()
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

    def setUp(self):
        super(BasicJSONAPITest, self).setUp()
        self._build_object()

        self.pk = self.content.pk
        url = '/api/en/{model}s/{pk}.json'.format(model=self.content._meta.module_name, pk=self.pk)
        self.response = self.client.get(url)
        self.result = json.loads(self.response.content)

    def _build_object(self):
        polygon = 'SRID=%s;MULTIPOLYGON(((0 0, 0 3, 3 3, 3 0, 0 0)))' % settings.SRID
        self.city = zoning_factories.CityFactory(geom=polygon)
        self.district = zoning_factories.DistrictFactory(geom=polygon)

        self.content = self.factory(geom='SRID=%s;POINT(1 1)' % settings.SRID)

        self.picture = common_factories.AttachmentFactory(obj=self.content,
                                                          attachment_file=get_dummy_uploaded_image())
        self.document = common_factories.AttachmentFactory(obj=self.content,
                                                           attachment_file=get_dummy_uploaded_document())
        self.video = common_factories.AttachmentFactory(obj=self.content, attachment_file='',
                                                        attachment_video='http://www.youtube.com/embed/Jm3anSjly0Y?wmode=opaque')
        self.video_detected = detect_backend(self.video.attachment_video)

        self.theme = common_factories.ThemeFactory()
        self.content.themes.add(self.theme)
        self.source = common_factories.RecordSourceFactory()
        self.content.source.add(self.source)

        path = core_factories.PathFactory(geom='SRID=%s;LINESTRING(0 10, 10 10)' % settings.SRID)
        self.trek = trekking_factories.TrekFactory(no_path=True)
        self.trek.add_path(path)
        self.poi = trekking_factories.POIFactory(no_path=True)
        self.poi.add_path(path, start=0.5, end=0.5)

    def test_thumbnail(self):
        self.assertEqual(self.result['thumbnail'],
                         os.path.join(settings.MEDIA_URL, self.picture.attachment_file.name) + '.120x120_q85_crop.png')

    def test_published_status(self):
        self.assertDictEqual(self.result['published_status'][0],
                             {u'lang': u'en', u'status': True, u'language': u'English'})

    def test_pictures(self):
        self.assertDictEqual(self.result['pictures'][0],
                             {u'url': os.path.join(settings.MEDIA_URL, self.picture.attachment_file.name) + '.800x800_q85.png',
                              u'title': self.picture.title,
                              u'legend': self.picture.legend,
                              u'author': self.picture.author})

    def test_files(self):
        self.assertDictEqual(self.result['files'][0],
                             {u'url': os.path.join(settings.MEDIA_URL, self.document.attachment_file.name),
                              u'title': self.document.title,
                              u'legend': self.document.legend,
                              u'author': self.document.author})

    def test_videos(self):
        self.assertDictEqual(self.result['videos'][0],
                             {u'backend': 'Youtube',
                              u'url': 'http://www.youtube.com/embed/Jm3anSjly0Y?wmode=opaque',
                              u'title': self.video.title,
                              u'legend': self.video.legend,
                              u'author': self.video.author,
                              u'code': self.video_detected.code})

    def test_cities(self):
        self.assertDictEqual(self.result['cities'][0],
                             {u"code": self.city.code,
                              u"name": self.city.name})

    def test_districts(self):
        self.assertDictEqual(self.result['districts'][0],
                             {u"id": self.district.id,
                              u"name": self.district.name})

    def test_themes(self):
        self.assertDictEqual(self.result['themes'][0],
                             {u"id": self.theme.id,
                              u"pictogram": os.path.join(settings.MEDIA_URL, self.theme.pictogram.name),
                              u"label": self.theme.label})

    def test_treks(self):
        self.assertDictEqual(self.result['treks'][0], {
            u'id': self.trek.id,
            u'category_id': 'T'})

    def test_pois(self):
        self.assertDictEqual(self.result['pois'][0], {
            u'id': self.poi.id,
            u'slug': self.poi.slug,
            u'name': self.poi.name,
            u'type': {
                u'id': self.poi.type.id,
                u'label': self.poi.type.label,
                u'pictogram': os.path.join(settings.MEDIA_URL, self.poi.type.pictogram.name)}})

    def test_sources(self):
        self.assertDictEqual(self.result['source'][0], {
            u'name': self.source.name,
            u'website': self.source.website,
            u"pictogram": os.path.join(settings.MEDIA_URL, self.source.pictogram.name)})

    def test_approved(self):
        self.assertFalse(self.result['approved'])


class TouristicContentAPITest(BasicJSONAPITest, TrekkingManagerTest):
    factory = TouristicContentFactory

    def _build_object(self):
        super(TouristicContentAPITest, self)._build_object()
        self.category = self.content.category
        self.type1 = TouristicContentTypeFactory(category=self.category)
        self.type2 = TouristicContentTypeFactory(category=self.category, pictogram=None)
        self.content.type1.add(self.type1)
        self.content.type2.add(self.type2)

    def test_expected_properties(self):
        self.assertEqual(sorted([
            'approved', 'areas', 'category', 'cities', 'contact',
            'description', 'description_teaser', 'districts', 'email',
            'filelist_url', 'files', 'id', 'map_image_url', 'name', 'pictures',
            'pois', 'practical_info', 'printable', 'publication_date',
            'published', 'published_status', 'reservation_id', 'reservation_system',
            'slug', 'source', 'themes', 'thumbnail', 'touristic_contents',
            'touristic_events', 'treks', 'type1', 'type2', 'videos', 'website', ]),
            sorted(self.result.keys()))

    def test_type1(self):
        self.assertDictEqual(self.result['type1'][0],
                             {u"id": self.type1.id,
                              u"name": self.type1.label,
                              u'pictogram': os.path.join(settings.MEDIA_URL, self.type1.pictogram.name),
                              u"in_list": self.type1.in_list})

    def test_type2(self):
        self.assertDictEqual(self.result['type2'][0],
                             {u"id": self.type2.id,
                              u"name": self.type2.label,
                              u'pictogram': None,
                              u"in_list": self.type2.in_list})

    def test_category(self):
        self.assertDictEqual(self.result['category'], {
            u"id": self.category.prefixed_id,
            u"order": None,
            u"label": self.category.label,
            u"slug": u"touristic-content",
            u"type1_label": self.category.type1_label,
            u"type2_label": self.category.type2_label,
            u"pictogram": os.path.join(settings.MEDIA_URL, self.category.pictogram.name)})


class TouristicEventAPITest(BasicJSONAPITest, TrekkingManagerTest):
    factory = TouristicEventFactory

    def test_expected_properties(self):
        self.assertEqual([
            'accessibility', 'approved', 'areas', 'begin_date', 'booking', 'category',
            'cities', 'contact', 'description', 'description_teaser',
            'districts', 'duration', 'email', 'end_date', 'filelist_url', 'files',
            'id', 'map_image_url', 'meeting_point', 'meeting_time', 'name',
            'organizer', 'participant_number', 'pictures', 'pois', 'practical_info',
            'printable', 'publication_date', 'published', 'published_status',
            'slug', 'source', 'speaker', 'target_audience', 'themes', 'thumbnail',
            'touristic_contents', 'touristic_events', 'treks', 'type',
            'type1', 'videos', 'website'],
            sorted(self.result.keys()))

    def test_type(self):
        self.assertDictEqual(self.result['type'],
                             {u"id": self.content.type.id,
                              u'pictogram': os.path.join(settings.MEDIA_URL, self.content.type.pictogram.name),
                              u"name": self.content.type.type})

    def test_type1(self):
        self.assertDictEqual(self.result['type1'][0],
                             {u"id": self.content.type.id,
                              u'pictogram': os.path.join(settings.MEDIA_URL, self.content.type.pictogram.name),
                              u"name": self.content.type.type})

    def test_category(self):
        self.assertDictEqual(self.result['category'],
                             {u"id": 'E',
                              u"order": None,
                              u"label": u"Touristic events",
                              u"slug": u"touristic-event",
                              u"type1_label": u"Type",
                              u"pictogram": u"/static/tourism/touristicevent.svg"})


class TouristicEventViewsSameStructureTests(AuthentFixturesTest):
    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        user = profile.user
        user.groups.add(Group.objects.get(name=u"Référents communication"))
        self.client.login(username=user.username, password='dooh')
        self.event1 = TouristicEventFactory.create()
        structure = StructureFactory.create()
        self.event2 = TouristicEventFactory.create(structure=structure)

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


class TouristicContentCustomViewTests(TrekkingManagerTest):
    @unittest.skipIf(settings.MAPENTITY_CONFIG.get('MAPENTITY_WEASYPRINT', False), "weasyprint mode")
    def test_overriden_document(self):
        content = TouristicContentFactory.create(published=True)

        with open(content.get_map_image_path(), 'w') as f:
            f.write('***' * 1000)

        url = '/api/en/touristiccontents/{pk}/slug.odt'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) > 1000)

        AttachmentFactory.create(obj=content, title="docprint", attachment_file=get_dummy_uploaded_document(size=100))
        url = '/api/en/touristiccontents/{pk}/slug.odt'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) < 1000)

    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        content = TouristicContentFactory.create(published=True)

        with open(content.get_map_image_path(), 'w') as f:
            f.write('***' * 1000)

        mocked.return_value.status_code = 200

        response = self.client.get(
            reverse('tourism:touristiccontent_printable',
                    kwargs={'lang': settings.LANGUAGE_CODE,
                            'pk': content.pk,
                            'slug': 'slug', })
        )
        self.assertEqual(response.status_code, 200)

    @unittest.skipIf(settings.MAPENTITY_CONFIG.get('MAPENTITY_WEASYPRINT', False), "weasyprint mode")
    def test_not_published_document(self):
        content = TouristicContentFactory.create(published=False)
        url = '/api/en/touristiccontents/{pk}/slug.odt'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_not_published_document_pdf(self):
        content = TouristicContentFactory.create(published=False)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TouristicEventCustomViewTests(TrekkingManagerTest):
    @unittest.skipIf(settings.MAPENTITY_CONFIG.get('MAPENTITY_WEASYPRINT', False), "weasyprint mode")
    def test_overriden_document(self):
        event = TouristicEventFactory.create(published=True)

        with open(event.get_map_image_path(), 'w') as f:
            f.write('***' * 1000)

        url = '/api/en/touristicevents/{pk}/slug.odt'.format(pk=event.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) > 1000)

        AttachmentFactory.create(obj=event, title="docprint", attachment_file=get_dummy_uploaded_document(size=100))
        url = '/api/en/touristicevents/{pk}/slug.odt'.format(pk=event.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) < 1000)

    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        content = TouristicEventFactory.create(published=True)

        with open(content.get_map_image_path(), 'w') as f:
            f.write('***' * 1000)

        mocked.return_value.status_code = 200
        response = self.client.get(
            reverse('tourism:touristicevent_printable',
                    kwargs={'lang': settings.LANGUAGE_CODE,
                            'pk': content.pk,
                            'slug': 'slug', })
        )
        self.assertEqual(response.status_code, 200)

    @unittest.skipIf(settings.MAPENTITY_CONFIG.get('MAPENTITY_WEASYPRINT', False), "weasyprint mode")
    def test_not_published_document_odt(self):
        content = TouristicEventFactory.create(published=False)
        url = '/api/en/touristicevents/{pk}/slug.odt'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_not_published_document_pdf(self):
        content = TouristicEventFactory.create(published=False)
        url = '/api/en/touristicevents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TouristicEventViewSetTest(TestCase):
    def test_touristic_events_without_enddate_filter(self):
        TouristicEventFactory.create_batch(10, published=True)
        response = self.client.get('/api/en/touristicevents.geojson')
        geojson = json.loads(response.content)
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
        geojson = json.loads(response.content)

        self.assertEqual(len(geojson['features']), 10)


class TouristicContentCategoryViewSetTest(TestCase):
    def test_get_categories(self):
        """
        Test category json serialization via api
        """
        nb_elements = 10
        TouristicContentCategoryFactory.create_batch(nb_elements)
        response = self.client.get(reverse('tourism:touristic_categories_json', kwargs={'lang': 'en'}))
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), nb_elements)


class InformationDeskAPITest(TestCase):
    def test_json(self):
        InformationDeskFactory.create()
        desk2 = InformationDeskFactory.create()
        response = self.client.get('/api/en/information_desks-{}.geojson'.format(desk2.type.id))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertIn('features', result)
        self.assertEqual(len(result['features']), 1)
        self.assertEqual(result['features'][0]['type'], 'Feature')
        self.assertEqual(result['features'][0]['geometry']['type'], 'Point')
        self.assertEqual(result['features'][0]['properties']['name'], desk2.name)
