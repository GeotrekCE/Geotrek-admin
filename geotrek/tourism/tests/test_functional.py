from django.contrib.gis.geos import Polygon, MultiPolygon
from django.conf import settings
from django.test.utils import override_settings
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string

import filecmp
from geotrek.authent.tests.factories import StructureFactory
from geotrek.authent.tests.factories import TrekkingManagerFactory
from geotrek.common.tests.factories import AttachmentFactory
from geotrek.common.tests import CommonTest
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.tourism.tests.factories import (TouristicContentFactory,
                                             TouristicContentCategoryFactory,
                                             TouristicEventFactory)
from geotrek.zoning.tests.factories import CityFactory

from unittest.mock import patch
import os


class TouristicContentViewsTests(CommonTest):
    model = TouristicContent
    modelfactory = TouristicContentFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}
    extra_column_list = ['type1', 'type2', 'eid']

    def get_expected_json_attrs(self):
        return {
            'accessibility': 'Accessible',
            'approved': False,
            'areas': [],
            'category': {
                'id': 'C{}'.format(self.obj.category.pk),
                'label': 'Category',
                'order': None,
                'pictogram': '/media/upload/touristiccontent-category.png',
                'slug': 'touristic-content',
                'type1_label': 'Type1 label',
                'type2_label': '',
            },
            'cities': [],
            'contact': '',
            'description': '<p>Blah CT</p>',
            'description_teaser': '',
            'districts': [],
            'dives': [],
            'email': None,
            'filelist_url': '/paperclip/get/tourism/touristiccontent/{}/'.format(self.obj.pk),
            'files': [],
            'label_accessibility': {
                'id': self.obj.label_accessibility.pk,
                'label': self.obj.label_accessibility.label,
                'pictogram': '/media/upload/dummy_img.png'
            },
            'map_image_url': '/image/touristiccontent-{}.png'.format(self.obj.pk),
            'name': 'Touristic content',
            'pictures': [],
            'pois': [],
            'portal': [{
                'name': self.obj.portal.get().name,
                'website': self.obj.portal.get().website
            }],
            'practical_info': '',
            'printable': '/api/en/touristiccontents/{}/touristic-content.pdf'.format(self.obj.pk),
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False},
            ],
            'reservation_id': 'XXXXXXXXX',
            'reservation_system': self.obj.reservation_system.name,
            'slug': 'touristic-content',
            'source': [],
            'structure': {'id': self.obj.structure.pk, 'name': 'My structure'},
            'themes': [{
                'id': self.obj.themes.get().pk,
                'label': self.obj.themes.get().label,
                'pictogram': self.obj.themes.get().pictogram.url,
            }],
            'thumbnail': None,
            'touristic_contents': [],
            'touristic_events': [],
            'treks': [],
            'type1': [{
                'id': self.obj.type1.get().pk,
                'in_list': 1,
                'name': 'Type1',
                'pictogram': '/media/upload/touristiccontent-type1.png'
            }],
            'type2': [{
                'id': self.obj.type2.get().pk,
                'in_list': 2,
                'name': 'Type2',
                'pictogram': '/media/upload/touristiccontent-type2.png'
            }],
            'videos': [],
            'website': None,
        }

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': StructureFactory.create().pk,
            'name_en': 'test',
            'category': TouristicContentCategoryFactory.create().pk,
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }

    def test_intersection_zoning(self):
        self.modelfactory.create()
        CityFactory.create(name="Are", code='09000',
                           geom=MultiPolygon(Polygon(((0, 0), (300, 0), (300, 100), (200, 100), (0, 0)),
                                                     srid=settings.SRID)))
        CityFactory.create(name="Nor", code='09001',
                           geom=MultiPolygon(Polygon(((200, 0), (300, 0), (300, 100), (200, 100), (200, 0)),
                                                     srid=settings.SRID)))
        params = '?city=09000'
        response = self.client.get(self.model.get_jsonlist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["object_list"]), 1)
        params = '?city=09001'
        response = self.client.get(self.model.get_jsonlist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["object_list"]), 0)

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'touristic_content_view': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List')().columns,
                             ['id', 'name', 'type1', 'type2', 'eid'])

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'touristic_content_export': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList')().columns,
                             ['id', 'type1', 'type2', 'eid'])


class TouristicEventViewsTests(CommonTest):
    model = TouristicEvent
    modelfactory = TouristicEventFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}
    extra_column_list = ['type', 'eid', 'themes']

    def get_expected_json_attrs(self):
        return {
            'accessibility': '',
            'approved': False,
            'areas': [],
            'begin_date': '2002-02-20',
            'booking': '',
            'category': {
                'id': 'E',
                'label': 'Touristic events',
                'order': 99,
                'pictogram': '/static/tourism/touristicevent.svg',
                'slug': 'touristic-event',
                'type1_label': 'Type',
            },
            'cities': [],
            'contact': '',
            'description': '',
            'description_teaser': '',
            'districts': [],
            'dives': [],
            'duration': '',
            'email': None,
            'end_date': '2202-02-22',
            'filelist_url': '/paperclip/get/tourism/touristicevent/{}/'.format(self.obj.pk),
            'files': [],
            'map_image_url': '/image/touristicevent-{}.png'.format(self.obj.pk),
            'meeting_point': '',
            'meeting_time': None,
            'name': 'Touristic event',
            'organizer': '',
            'participant_number': '',
            'pictures': [],
            'pois': [],
            'portal': [],
            'practical_info': '',
            'printable': '/api/en/touristicevents/{}/touristic-event.pdf'.format(self.obj.pk),
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False},
            ],
            'slug': 'touristic-event',
            'source': [],
            'speaker': '',
            'structure': {'id': self.obj.structure.pk, 'name': 'My structure'},
            'target_audience': None,
            'themes': [{
                'id': self.obj.themes.get().pk,
                'label': self.obj.themes.get().label,
                'pictogram': self.obj.themes.get().pictogram.url,
            }],
            'thumbnail': None,
            'touristic_contents': [],
            'touristic_events': [],
            'treks': [],
            'type': {
                'id': self.obj.type1[0].pk,
                'name': 'Type',
                'pictogram': '/media/upload/touristicevent-type.png'
            },
            'type1': [{
                'id': self.obj.type1[0].pk,
                'name': 'Type',
                'pictogram': '/media/upload/touristicevent-type.png'
            }],
            'videos': [],
            'website': None,
        }

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': StructureFactory.create().pk,
            'name_en': 'test',
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }

    @patch('mapentity.helpers.requests')
    def test_document_export_with_attachment(self, mock_requests):
        obj = self.modelfactory.create()
        attachment = AttachmentFactory.create(content_object=obj,
                                              attachment_file=get_dummy_uploaded_image(),
                                              title='mapimage')
        obj.attachment = attachment
        obj.save()
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = '<p id="properties">Mock</p>'
        response = self.client.get(obj.get_document_url())
        self.assertEqual(response.status_code, 200)
        element_in_dir = os.listdir(os.path.join(settings.MEDIA_ROOT, 'maps'))
        first_path = os.path.join(settings.MEDIA_ROOT, 'maps', element_in_dir[0])
        second_path = os.path.join(settings.MEDIA_ROOT, attachment.attachment_file.name)
        self.assertTrue(filecmp.cmp(first_path, second_path))

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'touristic_event_view': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List')().columns,
                             ['id', 'name', 'type', 'eid', 'themes'])

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'touristic_event_export': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList')().columns,
                             ['id', 'type', 'eid', 'themes'])
