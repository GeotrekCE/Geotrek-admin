from django.test.utils import override_settings
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string
from rest_framework.reverse import reverse

from geotrek.common.tests import CommonTest
from ..forms import RegulatorySensitiveAreaForm
from ..models import SensitiveArea, Species
from .factories import SensitiveAreaFactory, SpeciesFactory, BiodivManagerFactory, RegulatorySensitiveAreaFactory


class SensitiveAreaViewsTests(CommonTest):
    model = SensitiveArea
    modelfactory = SensitiveAreaFactory
    userfactory = BiodivManagerFactory
    expected_json_geom = {
        'type': 'Polygon',
        'coordinates': [[[3.0, 46.5], [3.0, 46.500027], [3.0000391, 46.500027],
                         [3.0000391, 46.5], [3.0, 46.5]]],
    }
    extra_column_list = ['description', 'contact']

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'published': self.obj.published,
            'radius': self.obj.radius,
            'species': self.obj.species_id,
        }

    def get_expected_datatables_attrs(self):
        return {
            'category': self.obj.category_display,
            'id': self.obj.pk,
            'species': self.obj.species_display,
        }

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

    def test_regulatory_form_creation(self):
        """Test if RegulatorySensitiveAreaForm is used with ?category query parameter"""
        response = self.client.get(self._get_add_url(), {'category': Species.REGULATORY})
        self.assertTrue(isinstance(response.context['form'], RegulatorySensitiveAreaForm))

    def test_regulatory_form_update(self):
        """Test if RegulatorySensitiveAreaForm is used with regulatory specie in update view"""
        obj = RegulatorySensitiveAreaFactory()
        response = self.client.get(obj.get_update_url())
        self.assertTrue(isinstance(response.context['form'], RegulatorySensitiveAreaForm))

    def test_kml_detail_view(self):
        sa = SensitiveAreaFactory()
        response = self.client.get(reverse('sensitivity:sensitivearea_kml_detail',
                                           kwargs={'lang': 'en', 'pk': sa.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.google-earth.kml+xml')
