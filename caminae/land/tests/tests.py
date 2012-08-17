from caminae.mapentity.tests import MapEntityTest
from caminae.authent.factories import PathManagerFactory

from caminae.common.factories import OrganismFactory
from caminae.land.models import (PhysicalEdge, LandEdge, CompetenceEdge,
    WorkManagementEdge, SignageManagementEdge)
from caminae.land.factories import (PhysicalEdgeFactory, LandEdgeFactory, 
    CompetenceEdgeFactory, WorkManagementEdgeFactory, SignageManagementEdgeFactory, 
    PhysicalTypeFactory, LandTypeFactory)


class PhysicalEdgeViewsTest(MapEntityTest):
    model = PhysicalEdge
    modelfactory = PhysicalEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        return {
            'physical_type': PhysicalTypeFactory.create().pk,
            'geom': '{"paths": [{"path": 1}]}',
        }


class LandEdgeViewsTest(MapEntityTest):
    model = LandEdge
    modelfactory = LandEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        return {
            'land_type': LandTypeFactory.create().pk,
            'geom': '{"paths": [{"path": 1}]}',
        }


class CompetenceEdgeViewsTest(MapEntityTest):
    model = CompetenceEdge
    modelfactory = CompetenceEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        return {
            'organization': OrganismFactory.create().pk,
            'geom': '{"paths": [{"path": 1}]}',
        }


class WorkManagementEdgeViewsTest(MapEntityTest):
    model = WorkManagementEdge
    modelfactory = WorkManagementEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        return {
            'organization': OrganismFactory.create().pk,
            'geom': '{"paths": [{"path": 1}]}',
        }



class SignageManagementEdgeViewsTest(MapEntityTest):
    model = SignageManagementEdge
    modelfactory = SignageManagementEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        return {
            'organization': OrganismFactory.create().pk,
            'geom': '{"paths": [{"path": 1}]}',
        }
