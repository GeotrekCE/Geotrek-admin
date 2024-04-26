from django.conf import settings

from geotrek.authent.tests.factories import PathManagerFactory
from geotrek.common.tests import CommonTest
from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.models import INFRASTRUCTURE_TYPES, Infrastructure
from geotrek.infrastructure.tests.factories import (
    InfrastructureConditionFactory,
    InfrastructureFactory,
    InfrastructureTypeFactory,
    PointInfrastructureFactory,
)


class InfrastructureViewsTest(CommonTest):
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
            'name': self.obj.name,
            'published': self.obj.published,
        }

    def get_expected_datatables_attrs(self):
        return {
            'cities': '',
            'conditions': self.obj.conditions_display,
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
            'conditions': [InfrastructureConditionFactory.create().pk],
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
            'conditions': [InfrastructureConditionFactory.create().pk],
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data['topology'] = '{"paths": [%s]}' % path.pk
        else:
            good_data['geom'] = 'POINT(0.42 0.666)'
        return good_data
