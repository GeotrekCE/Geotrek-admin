from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from geotrek.common.tests import CommonTest
from geotrek.authent.tests.factories import PathManagerFactory
from geotrek.core.tests.factories import PathFactory
from geotrek.common.tests.factories import OrganismFactory
from geotrek.land.models import (PhysicalEdge, LandEdge, CompetenceEdge,
                                 WorkManagementEdge, SignageManagementEdge)
from geotrek.land.tests.factories import (PhysicalEdgeFactory, LandEdgeFactory,
                                          CompetenceEdgeFactory, WorkManagementEdgeFactory,
                                          SignageManagementEdgeFactory, PhysicalTypeFactory,
                                          LandTypeFactory)


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
    get_expected_json_attrs = None  # Disable API tests
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'checkbox', 'physical_type', 'eid']
    expected_column_formatlist_extra = ['id', 'physical_type', 'eid']

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
            'length_2d': round(self.obj.length, 1),
            'checkbox': self.obj.checkbox_display
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class LandEdgeViewsTest(CommonTest):
    model = LandEdge
    modelfactory = LandEdgeFactory
    userfactory = PathManagerFactory
    get_expected_json_attrs = None  # Disable API tests
    extra_column_list = ['owner', 'agreement']
    expected_column_list_extra = ['id', 'checkbox', 'land_type', 'owner', 'agreement']
    expected_column_formatlist_extra = ['id', 'owner', 'agreement']

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
            'length_2d': round(self.obj.length, 1),
            'checkbox': self.obj.checkbox_display
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class CompetenceEdgeViewsTest(CommonTest):
    model = CompetenceEdge
    modelfactory = CompetenceEdgeFactory
    userfactory = PathManagerFactory
    get_expected_json_attrs = None  # Disable API tests
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'checkbox', 'organization', 'eid']
    expected_column_formatlist_extra = ['id', 'organization', 'eid']

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
            'length_2d': round(self.obj.length, 1),
            'checkbox': self.obj.checkbox_display
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class WorkManagementEdgeViewsTest(CommonTest):
    model = WorkManagementEdge
    modelfactory = WorkManagementEdgeFactory
    userfactory = PathManagerFactory
    get_expected_json_attrs = None  # Disable API tests
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'checkbox', 'organization', 'eid']
    expected_column_formatlist_extra = ['id', 'organization', 'eid']

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
            'length_2d': round(self.obj.length, 1),
            'checkbox': self.obj.checkbox_display
        }


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class SignageManagementEdgeViewsTest(CommonTest):
    model = SignageManagementEdge
    modelfactory = SignageManagementEdgeFactory
    userfactory = PathManagerFactory
    get_expected_json_attrs = None  # Disable API tests
    extra_column_list = ['eid']
    expected_column_list_extra = ['id', 'checkbox', 'organization', 'eid']
    expected_column_formatlist_extra = ['id', 'organization', 'eid']

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
            'length_2d': round(self.obj.length, 1),
            'checkbox': self.obj.checkbox_display
        }
