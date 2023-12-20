from django.contrib.gis.geos import Polygon, MultiPolygon
from django.conf import settings
from django.test.utils import override_settings
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string

import filecmp
from geotrek.authent.tests.factories import StructureFactory
from geotrek.authent.tests.factories import TrekkingManagerFactory
from geotrek.common.tests.factories import AttachmentFactory
from geotrek.common.tests import CommonTest, GeotrekAPITestCase
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.tourism.models import (TouristicContent,
                                    TouristicEvent)
from geotrek.tourism.tests.factories import (TouristicContentFactory,
                                             TouristicContentCategoryFactory,
                                             TouristicEventFactory,
                                             TouristicEventParticipantCountFactory,
                                             TouristicEventParticipantCategoryFactory)
from geotrek.zoning.tests.factories import CityFactory

from unittest.mock import patch
import os
import csv
from io import StringIO
from operator import attrgetter


class TouristicContentViewsTests(GeotrekAPITestCase, CommonTest):
    model = TouristicContent
    modelfactory = TouristicContentFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}
    extra_column_list = ['type1', 'type2', 'eid']

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

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

    def get_expected_datatables_attrs(self):
        return {
            'category': self.obj.category.label,
            'id': self.obj.pk,
            'name': self.obj.name_display
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
        response = self.client.get(self.model.get_datatablelist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["recordsFiltered"], 1)
        params = '?city=09001'
        response = self.client.get(self.model.get_datatablelist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 0)

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


class TouristicEventViewsTests(GeotrekAPITestCase, CommonTest):
    model = TouristicEvent
    modelfactory = TouristicEventFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}
    extra_column_list = ['type', 'eid', 'themes']

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

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
            'start_time': None,
            'end_time': None,
            'name': 'Touristic event',
            'organizer': None,
            'capacity': None,
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

    def get_expected_datatables_attrs(self):
        return {
            'begin_date': '20/02/2002',
            'end_date': '22/02/2202',
            'id': self.obj.pk,
            'name': self.obj.name_display,
            'type': self.obj.type.type
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
            'begin_date': '2002-02-20',
            'end_date': '2002-02-20'
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

    def test_participant_models(self):
        category = TouristicEventParticipantCategoryFactory()
        self.assertEqual(str(category), category.label)

        count = TouristicEventParticipantCountFactory()
        self.assertEqual(str(count), f"{count.count} {count.category}")

    def test_form_with_participant_categories(self):
        category = TouristicEventParticipantCategoryFactory()
        event = self.modelfactory.create()
        response = self.client.get(event.get_update_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, category.label)

    def test_event_with_participant_categories(self):
        categories = TouristicEventParticipantCategoryFactory.create_batch(2)

        data = self.get_good_data()
        data.update({
            'participant_count_{}'.format(categories[0].pk): 10,
        })
        response = self.client.post(self._get_add_url(), data)
        self.assertEqual(response.status_code, 302)
        event = TouristicEvent.objects.last()
        self.assertEqual(event.participants.count(), 1)
        count = event.participants.first()
        self.assertEqual(count.count, 10)
        self.assertEqual(count.category, categories[0])

        data.update({
            'participant_count_{}'.format(categories[1].pk): 20,
        })
        response = self.client.post(event.get_update_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(event.participants.count(), 2)

        data.pop('participant_count_{}'.format(categories[0].pk))
        response = self.client.post(event.get_update_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(event.participants.count(), 1)
        count = event.participants.first()
        self.assertEqual(count.count, 20)
        self.assertEqual(count.category, categories[1])

    def test_csv_participants_count(self):
        event = self.modelfactory.create()
        counts = TouristicEventParticipantCountFactory.create_batch(2, event=event)
        total_count = sum(map(attrgetter('count'), counts))
        self.assertEqual(event.participants_total, total_count)
        self.assertEqual(event.participants_total_verbose_name, "Number of participants")
        with self.assertNumQueries(16):
            response = self.client.get(event.get_format_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        for row in reader:
            if row['ID'] == event.pk:
                self.assertEqual(row['Number of participants'], total_count)
