# -*- coding: utf-8 -*-
import os
import json

import mock

from datetime import datetime
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings
from django.test import TestCase

from geotrek.authent.factories import StructureFactory, UserProfileFactory
from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.trekking.tests import TrekkingManagerTest
from geotrek.core import factories as core_factories
from geotrek.trekking import factories as trekking_factories
from geotrek.zoning import factories as zoning_factories
from geotrek.common import factories as common_factories
from geotrek.common.tests import TranslationResetMixin
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_document
from geotrek.tourism.factories import (InformationDeskFactory,
                                       TouristicContentFactory,
                                       TouristicEventFactory,
                                       TouristicContentCategoryFactory,
                                       TouristicContentTypeFactory)
from embed_video.backends import detect_backend


PNG_BLACK_PIXEL = bytes.fromhex('89504e470d0a1a0a0000000d494844520000000100000001080400000'
                                '0b51c0c020000000b4944415478da6364f80f00010501012718e3660000000049454e44'
                                'ae426082')


class TouristicContentViewsSameStructureTests(AuthentFixturesTest):
    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        user = profile.user
        user.groups.add(Group.objects.get(name="Référents communication"))
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
        url = '/api/en/{model}s/{pk}.json'.format(model=self.content._meta.model_name, pk=self.pk)
        self.response = self.client.get(url)
        self.result = json.loads(self.response.content.decode())

    def _build_object(self):
        polygon = 'SRID=%s;MULTIPOLYGON(((0 0, 0 3, 3 3, 3 0, 0 0)))' % settings.SRID
        self.city = zoning_factories.CityFactory(geom=polygon)
        self.district = zoning_factories.DistrictFactory(geom=polygon)

        self.content = self.factory(geom='SRID=%s;POINT(1 1)' % settings.SRID)

        self.picture = common_factories.AttachmentFactory(content_object=self.content,
                                                          attachment_file=get_dummy_uploaded_image())
        self.document = common_factories.AttachmentFactory(content_object=self.content,
                                                           attachment_file=get_dummy_uploaded_document())
        self.video = common_factories.AttachmentFactory(content_object=self.content, attachment_file='',
                                                        attachment_video='http://www.youtube.com/embed/Jm3anSjly0Y?wmode=opaque')
        self.video_detected = detect_backend(self.video.attachment_video)

        self.theme = common_factories.ThemeFactory()
        self.content.themes.add(self.theme)
        self.source = common_factories.RecordSourceFactory()
        self.content.source.add(self.source)

        self.portal = common_factories.TargetPortalFactory()
        self.content.portal.add(self.portal)

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
                             {'lang': 'en', 'status': True, 'language': 'English'})

    def test_pictures(self):
        self.assertDictEqual(self.result['pictures'][0],
                             {'url': os.path.join(settings.MEDIA_URL, self.picture.attachment_file.name) + '.800x800_q85.png',
                              'title': self.picture.title,
                              'legend': self.picture.legend,
                              'author': self.picture.author})

    def test_files(self):
        self.assertDictEqual(self.result['files'][0],
                             {'url': os.path.join(settings.MEDIA_URL, self.document.attachment_file.name),
                              'title': self.document.title,
                              'legend': self.document.legend,
                              'author': self.document.author})

    def test_videos(self):
        self.assertDictEqual(self.result['videos'][0],
                             {'backend': 'Youtube',
                              'url': 'http://www.youtube.com/embed/Jm3anSjly0Y?wmode=opaque',
                              'title': self.video.title,
                              'legend': self.video.legend,
                              'author': self.video.author,
                              'code': self.video_detected.code})

        self.video = common_factories.AttachmentFactory(
            content_object=self.content, attachment_file='',
            attachment_video='http://www.dailymotion.com/video/x6e0q24')
        self.video_detected = detect_backend(self.video.attachment_video)
        self.pk = self.content.pk
        url = '/api/en/{model}s/{pk}.json'.format(model=self.content._meta.model_name, pk=self.pk)
        self.response = self.client.get(url)
        self.result = json.loads(self.response.content)
        self.assertDictEqual(self.result['videos'][0],
                             {'backend': 'Dailymotion',
                              'url': 'http://www.dailymotion.com/embed/video/x6e0q24',
                              'title': self.video.title,
                              'legend': self.video.legend,
                              'author': self.video.author,
                              'code': self.video_detected.code})

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

    def _build_object(self):
        super(TouristicContentAPITest, self)._build_object()
        self.category = self.content.category
        self.type1 = TouristicContentTypeFactory(category=self.category, in_list=1)
        self.type2 = TouristicContentTypeFactory(category=self.category, in_list=1, pictogram=None)
        self.content.type1.add(self.type1)
        self.content.type2.add(self.type2)

    def test_expected_properties(self):
        self.assertEqual(sorted([
            'approved', 'areas', 'category', 'cities', 'contact',
            'description', 'description_teaser', 'districts', 'email',
            'filelist_url', 'files', 'id', 'map_image_url', 'name', 'pictures',
            'pois', 'practical_info', 'printable', 'publication_date',
            'published', 'published_status', 'reservation_id', 'reservation_system',
            'slug', 'source', 'portal', 'themes', 'thumbnail', 'touristic_contents',
            'touristic_events', 'treks', 'type1', 'type2', 'videos', 'website']),
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
            "type1_label": self.category.type1_label,
            "type2_label": self.category.type2_label,
            "pictogram": os.path.join(settings.MEDIA_URL, self.category.pictogram.name)})


class TouristicEventAPITest(BasicJSONAPITest, TrekkingManagerTest):
    factory = TouristicEventFactory

    def test_expected_properties(self):
        self.assertEqual(sorted([
            'accessibility', 'approved', 'areas', 'begin_date', 'booking', 'category',
            'cities', 'contact', 'description', 'description_teaser',
            'districts', 'duration', 'email', 'end_date', 'filelist_url', 'files',
            'id', 'map_image_url', 'meeting_point', 'meeting_time', 'name',
            'organizer', 'participant_number', 'pictures', 'pois', 'portal', 'practical_info',
            'printable', 'publication_date', 'published', 'published_status',
            'slug', 'source', 'speaker', 'target_audience', 'themes',
            'thumbnail', 'touristic_contents', 'touristic_events', 'treks', 'type',
            'type1', 'videos', 'website']),
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
    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        user = profile.user
        user.groups.add(Group.objects.get(name="Référents communication"))
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

    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        content = TouristicContentFactory.create(published=True)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_not_published_document_pdf(self):
        content = TouristicContentFactory.create(published=False)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


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
        geojson = json.loads(response.content.decode())
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
        geojson = json.loads(response.content.decode())

        self.assertEqual(len(geojson['features']), 10)


class TouristicContentCategoryViewSetTest(TestCase):
    def test_get_categories(self):
        """
        Test category json serialization via api
        """
        nb_elements = 10
        TouristicContentCategoryFactory.create_batch(nb_elements)
        response = self.client.get(reverse('tourism:touristic_categories_json', kwargs={'lang': 'en'}))
        json_response = json.loads(response.content.decode())
        self.assertEqual(len(json_response), nb_elements)


class InformationDeskAPITest(TestCase):
    def test_geojson(self):
        InformationDeskFactory.create()
        desk2 = InformationDeskFactory.create()
        response = self.client.get('/api/en/information_desks-{}.geojson'.format(desk2.type.id))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode())
        self.assertIn('features', result)
        self.assertEqual(len(result['features']), 1)
        self.assertEqual(result['features'][0]['type'], 'Feature')
        self.assertEqual(result['features'][0]['geometry']['type'], 'Point')
        self.assertEqual(result['features'][0]['properties']['name'], desk2.name)
