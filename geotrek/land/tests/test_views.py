from django.test import TestCase

from geotrek.common.tests import CommonTest
from geotrek.authent.factories import PathManagerFactory
from geotrek.core.factories import PathFactory, PathAggregationFactory
from geotrek.common.factories import OrganismFactory
from geotrek.land.models import (PhysicalEdge, LandEdge, CompetenceEdge,
                                 WorkManagementEdge, SignageManagementEdge)
from geotrek.land.factories import (PhysicalEdgeFactory, LandEdgeFactory,
                                    CompetenceEdgeFactory, WorkManagementEdgeFactory,
                                    SignageManagementEdgeFactory, PhysicalTypeFactory,
                                    LandTypeFactory)


class EdgeHelperTest(TestCase):

    factory = None
    helper_name = None

    def test_path_helpers(self):
        if not self.factory:
            return   # ignore abstract test
        p = PathFactory.create()
        self.assertEquals(len(getattr(p, self.helper_name)), 0)
        e = self.factory.create(no_path=True)
        PathAggregationFactory.create(topo_object=e, path=p)
        self.assertEqual([o.pk for o in getattr(p, self.helper_name).all()],
                         [e.pk])


class LandEdgeTest(EdgeHelperTest):

    factory = LandEdgeFactory
    helper_name = 'land_edges'


class PhysicalEdgeTest(EdgeHelperTest):

    factory = PhysicalEdgeFactory
    helper_name = 'physical_edges'


class CompetenceEdgeTest(EdgeHelperTest):

    factory = CompetenceEdgeFactory
    helper_name = 'competence_edges'


class WorkManagementEdgeTest(EdgeHelperTest):

    factory = WorkManagementEdgeFactory
    helper_name = 'work_edges'


class SignageManagementEdgeTest(EdgeHelperTest):

    factory = SignageManagementEdgeFactory
    helper_name = 'signage_edges'


class PhysicalEdgeViewsTest(CommonTest):
    model = PhysicalEdge
    modelfactory = PhysicalEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'physical_type': PhysicalTypeFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }


class LandEdgeViewsTest(CommonTest):
    model = LandEdge
    modelfactory = LandEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'land_type': LandTypeFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }


class CompetenceEdgeViewsTest(CommonTest):
    model = CompetenceEdge
    modelfactory = CompetenceEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }


class WorkManagementEdgeViewsTest(CommonTest):
    model = WorkManagementEdge
    modelfactory = WorkManagementEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }


class SignageManagementEdgeViewsTest(CommonTest):
    model = SignageManagementEdge
    modelfactory = SignageManagementEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }
