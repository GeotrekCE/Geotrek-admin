from django.test.utils import override_settings
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string

from geotrek.common.tests import CommonTest, GeotrekAPITestCase
from geotrek.sensitivity.models import SensitiveArea
from geotrek.sensitivity.tests.factories import (SensitiveAreaFactory, SpeciesFactory, SportPracticeFactory,
                                                 RegulatorySensitiveAreaFactory, BiodivManagerFactory)


class SensitiveAreaViewsTests(GeotrekAPITestCase, CommonTest):
    model = SensitiveArea
    modelfactory = SensitiveAreaFactory
    userfactory = BiodivManagerFactory
    expected_json_geom = {
        'type': 'Polygon',
        'coordinates': [[[3.0, 46.5], [3.0, 46.500027], [3.0000391, 46.500027], [3.0000391, 46.5], [3.0, 46.5]]],
    }
    extra_column_list = ['description', 'contact']

    def get_expected_json_attrs(self):
        return {
            'attachments': [],
            'contact': '<a href="mailto:toto@tata.com">toto@tata.com</a>',
            'description': 'Blabla',
            'kml_url': '/api/en/sensitiveareas/{}.kml'.format(self.obj.pk),
            'publication_date': '2020-03-17',
            'published': True,
            'species': {
                'id': self.obj.species.pk,
                'name': "Species",
                'period': [False, False, False, False, False, True, True, False, False, False, False, False],
                'pictogram': "/media/upload/dummy_img.png",
                'practices': [
                    {'id': self.obj.species.practices.all()[0].pk, 'name': "Practice1"},
                    {'id': self.obj.species.practices.all()[1].pk, 'name': "Practice2"},
                ],
                'url': self.obj.species.url,
            },
        }

    def get_expected_datatables_attrs(self):
        return {
            'category': self.obj.category_display,
            'id': self.obj.pk,
            'species': self.obj.species_display
        }

    def setUp(self):
        translation.deactivate()
        super().setUp()

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'species': SpeciesFactory.create().pk,
            'geom': '{"type": "Polygon", "coordinates":[[[0, 0], [0, 1], [1, 0], [0, 0]]]}',
            'structure': str(self.user.profile.structure.pk),
        }

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'sensitivity_view': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List')().columns,
                             ['id', 'species', 'description', 'contact'])

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'sensitivity_export': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList')().columns,
                             ['id', 'description', 'contact'])


class RegulatorySensitiveAreaViewsTests(GeotrekAPITestCase, CommonTest):
    model = SensitiveArea
    modelfactory = RegulatorySensitiveAreaFactory
    userfactory = BiodivManagerFactory
    expected_json_geom = {
        'type': 'Polygon',
        'coordinates': [[[3.0, 46.5], [3.0, 46.500027], [3.0000391, 46.500027], [3.0000391, 46.5], [3.0, 46.5]]],
    }
    extra_column_list = ['description', 'contact']

    def get_expected_json_attrs(self):
        return {
            'attachments': [],
            'contact': '<a href="mailto:toto@tata.com">toto@tata.com</a>',
            'description': 'Blabla',
            'kml_url': '/api/en/sensitiveareas/{}.kml'.format(self.obj.pk),
            'publication_date': '2020-03-17',
            'published': True,
            'species': {
                'id': self.obj.species.pk,
                'name': "Species",
                'period': [False, False, False, False, False, True, True, False, False, False, False, False],
                'pictogram': "/media/upload/dummy_img.png",
                'practices': [
                    {'id': self.obj.species.practices.all()[0].pk, 'name': "Practice1"},
                    {'id': self.obj.species.practices.all()[1].pk, 'name': "Practice2"},
                ],
                'url': self.obj.species.url,
            },
        }

    def get_expected_datatables_attrs(self):
        return {
            'category': self.obj.category_display,
            'id': self.obj.pk,
            'species': self.obj.species_display,
        }

    def setUp(self):
        translation.deactivate()
        super().setUp()

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'name': 'Test',
            'practices': [SportPracticeFactory.create().pk],
            'geom': '{"type": "Polygon", "coordinates":[[[0, 0], [0, 1], [1, 0], [0, 0]]]}',
            'structure': str(self.user.profile.structure.pk),
        }

    def _get_add_url(self):
        return self.model.get_add_url() + '?category=2'

    def test_crud_status(self):
        if self.model is None:
            return  # Abstract test should not run

        obj = self.modelfactory()

        response = self.client.get(obj.get_list_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(obj.get_detail_url().replace(str(obj.pk), '1234567890'))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(obj.get_detail_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(obj.get_update_url())
        self.assertEqual(response.status_code, 200)

        self._post_update_form(obj)

        response = self.client.get(obj.get_delete_url())
        self.assertEqual(response.status_code, 200)

        url = obj.get_detail_url()
        obj.delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self._post_add_form()

        # Test to update without login
        self.logout()

        obj = self.modelfactory()

        response = self.client.get(self.model.get_add_url() + '?category=2')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(obj.get_update_url())
        self.assertEqual(response.status_code, 302)

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'sensitivity_view': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List')().columns,
                             ['id', 'species', 'description', 'contact'])

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'sensitivity_export': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList')().columns,
                             ['id', 'description', 'contact'])
