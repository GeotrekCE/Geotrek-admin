from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from geotrek.common.tests import CommonTest
from geotrek.authent.tests.factories import PathManagerFactory
from geotrek.core.tests.factories import PathFactory
from geotrek.common.tests.factories import OrganismFactory
from geotrek.land.models import (PhysicalEdge, LandEdge, CompetenceEdge,
                                 WorkManagementEdge, SignageManagementEdge,
                                 CirculationEdge)
from geotrek.land.tests.factories import (PhysicalEdgeFactory, LandEdgeFactory,
                                          CompetenceEdgeFactory, WorkManagementEdgeFactory,
                                          SignageManagementEdgeFactory, PhysicalTypeFactory,
                                          LandTypeFactory, CirculationEdgeFactory,
                                          CirculationTypeFactory, AuthorizationTypeFactory)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class EdgeHelperTest(TestCase):

    factory = None
    helper_name = None

    def test_path_helpers(self):
        if not self.factory:
            return   # ignore abstract test
        p = PathFactory.create()
        self.assertEqual(len(getattr(p, self.helper_name)), 0)
        e = self.factory.create(paths=[p])
        self.assertEqual([o.pk for o in getattr(p, self.helper_name).all()],
                         [e.pk])


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class LandEdgeTest(EdgeHelperTest):

    factory = LandEdgeFactory
    helper_name = 'land_edges'


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PhysicalEdgeTest(EdgeHelperTest):

    factory = PhysicalEdgeFactory
    helper_name = 'physical_edges'


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class CirculationEdgeTest(EdgeHelperTest):

    factory = CirculationEdgeFactory
    helper_name = 'circulation_edges'


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class CompetenceEdgeTest(EdgeHelperTest):

    factory = CompetenceEdgeFactory
    helper_name = 'competence_edges'


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class WorkManagementEdgeTest(EdgeHelperTest):

    factory = WorkManagementEdgeFactory
    helper_name = 'work_edges'


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class SignageManagementEdgeTest(EdgeHelperTest):

    factory = SignageManagementEdgeFactory
    helper_name = 'signage_edges'


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PhysicalEdgeViewsTest(CommonTest):
    model = PhysicalEdge
    modelfactory = PhysicalEdgeFactory
    userfactory = PathManagerFactory
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'physical_type', 'eid']
    expected_column_formatlist_extra = ['id', 'physical_type', 'eid']
    expected_json_geom = {'coordinates': [[3.0, 46.5], [3.001304, 46.5009004]],
                          'type': 'LineString'}

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name,
            'color_index': self.obj.physical_type_id
        }

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'physical_type': PhysicalTypeFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'length': round(self.obj.length, 1),
            'physical_type': self.obj.physical_type_display,
            'length_2d': round(self.obj.length, 1)
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class LandEdgeViewsTest(CommonTest):
    model = LandEdge
    modelfactory = LandEdgeFactory
    userfactory = PathManagerFactory
    extra_column_list = ['owner', 'agreement']
    expected_column_list_extra = ['id', 'land_type', 'owner', 'agreement']
    expected_column_formatlist_extra = ['id', 'owner', 'agreement']
    expected_json_geom = {'coordinates': [[3.0013501, 46.5008686],
                                          [3.0000461, 46.4999682]],
                          'type': 'LineString'}

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name,
            'color_index': self.obj.land_type_id
        }

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'land_type': LandTypeFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'land_type': self.obj.land_type_display,
            'length': round(self.obj.length, 1),
            'length_2d': round(self.obj.length, 1)
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class CirculationEdgeViewsTest(CommonTest):
    model = CirculationEdge
    modelfactory = CirculationEdgeFactory
    userfactory = PathManagerFactory
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'circulation_type', 'authorization_type', 'eid']
    expected_column_formatlist_extra = ['id', 'eid']
    expected_json_geom = {'coordinates': [[3.0, 46.5], [3.001304, 46.5009004]],
                          'type': 'LineString'}

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name,
            'color_index': self.obj.circulation_type_id
        }

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'circulation_type': CirculationTypeFactory.create().pk,
            'authorization_type': AuthorizationTypeFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'circulation_type': self.obj.circulation_type_display,
            'authorization_type': self.obj.authorization_type_display,
            'length': round(self.obj.length, 1),
            'length_2d': round(self.obj.length, 1)
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class CompetenceEdgeViewsTest(CommonTest):
    model = CompetenceEdge
    modelfactory = CompetenceEdgeFactory
    userfactory = PathManagerFactory
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'organization', 'eid']
    expected_column_formatlist_extra = ['id', 'organization', 'eid']
    expected_json_geom = {'coordinates': [[2.9999539, 46.5000318],
                                          [3.0012579, 46.5009323]],
                          'type': 'LineString'}

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name,
            'color_index': self.obj.organization_id
        }

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'length': round(self.obj.length, 1),
            'organization': self.obj.organization_display,
            'length_2d': round(self.obj.length, 1)
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class WorkManagementEdgeViewsTest(CommonTest):
    model = WorkManagementEdge
    modelfactory = WorkManagementEdgeFactory
    userfactory = PathManagerFactory
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'organization', 'eid']
    expected_column_formatlist_extra = ['id', 'organization', 'eid']
    expected_json_geom = {'coordinates': [[2.9999078, 46.5000637],
                                          [3.0012118, 46.5009641]],
                          'type': 'LineString'}

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name,
            'color_index': self.obj.organization_id
        }

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'length': round(self.obj.length, 1),
            'organization': self.obj.organization_display,
            'length_2d': round(self.obj.length, 1)
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class SignageManagementEdgeViewsTest(CommonTest):
    model = SignageManagementEdge
    modelfactory = SignageManagementEdgeFactory
    userfactory = PathManagerFactory
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'organization', 'eid']
    expected_column_formatlist_extra = ['id', 'organization', 'eid']
    expected_json_geom = {'coordinates': [[3.0013962, 46.5008368],
                                          [3.0000922, 46.4999363]],
                          'type': 'LineString'}

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name,
            'color_index': self.obj.organization_id
        }

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'length': round(self.obj.length, 1),
            'organization': self.obj.organization_display,
            'length_2d': round(self.obj.length, 1)
        }
