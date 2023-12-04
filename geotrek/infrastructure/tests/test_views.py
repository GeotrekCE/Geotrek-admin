from django.conf import settings

from geotrek.common.tests import CommonTest, GeotrekAPITestCase
from geotrek.authent.tests.factories import PathManagerFactory
from geotrek.infrastructure.models import (Infrastructure, INFRASTRUCTURE_TYPES)
from geotrek.infrastructure.filters import InfrastructureFilterSet
from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.tests.factories import (InfrastructureFactory, InfrastructureNoPictogramFactory,
                                                    InfrastructureTypeFactory, InfrastructureConditionFactory,
                                                    PointInfrastructureFactory)


class InfrastructureViewsTest(GeotrekAPITestCase, CommonTest):
    model = Infrastructure
    modelfactory = InfrastructureFactory
    userfactory = PathManagerFactory
    expected_json_geom = {'type': 'LineString', 'coordinates': [[3.0, 46.5], [3.001304, 46.5009004]]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'name', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'type', 'eid']

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
            'name': self.obj.name,
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False}
            ],
            'structure': {
                'id': self.obj.structure.pk,
                'name': self.obj.structure.name,
            },
            'type': {
                'id': self.obj.type.pk,
                'label': self.obj.type.label,
                'pictogram': self.obj.type.pictogram.url if self.obj.type.pictogram else '/static/infrastructure/picto-infrastructure.png',
            },
        }

    def get_expected_datatables_attrs(self):
        return {
            'cities': '',
            'condition': self.obj.condition.label,
            'id': self.obj.pk,
            'name': self.obj.name_display,
            'type': self.obj.type.label,
        }

    def get_good_data(self):
        good_data = {
            'name_fr': 'test',
            'name_en': 'test_en',
            'description': 'oh',
            'type': InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING).pk,
            'condition': InfrastructureConditionFactory.create().pk,
            'accessibility': 'description accessibility'
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data['topology'] = '{"paths": [%s]}' % path.pk
        else:
            good_data['geom'] = 'LINESTRING (0.0 0.0, 1.0 1.0)'
        return good_data

    def test_description_in_detail_page(self):
        infra = InfrastructureFactory.create(description="<b>Beautiful !</b>")
        response = self.client.get(infra.get_detail_url())
        self.assertContains(response, "<b>Beautiful !</b>")

    def test_check_structure_or_none_related_are_visible(self):
        infratype = InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING, structure=None)
        response = self.client.get(self.model.get_add_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        form = response.context['form']
        type = form.fields['type']
        self.assertTrue((infratype.pk, str(infratype)) in type.choices)

    def test_no_pictogram(self):
        self.modelfactory = InfrastructureNoPictogramFactory
        super().test_api_detail_for_model()


class PointInfrastructureViewsTest(InfrastructureViewsTest):
    modelfactory = PointInfrastructureFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [3.0, 46.5]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'name', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'type', 'eid']

    def get_good_data(self):
        good_data = {
            'accessibility': 'description accessibility',
            'name_fr': 'test',
            'name_en': 'test_en',
            'description': 'oh',
            'type': InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING).pk,
            'condition': InfrastructureConditionFactory.create().pk,
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data['topology'] = '{"paths": [%s]}' % path.pk
        else:
            good_data['geom'] = 'POINT(0.42 0.666)'
        return good_data


class InfrastructureFilterTest(CommonTest):
    factory = InfrastructureFactory
    filterset = InfrastructureFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = InfrastructureFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        infrastructure1 = InfrastructureFactory.create(provider='my_provider1')
        infrastructure2 = InfrastructureFactory.create(provider='my_provider2')

        filter_set = InfrastructureFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(infrastructure1, filter_set.qs)
        self.assertIn(infrastructure2, filter_set.qs)
