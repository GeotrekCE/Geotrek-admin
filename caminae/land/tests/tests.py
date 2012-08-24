from caminae.mapentity.tests import MapEntityTest
from caminae.authent.factories import PathManagerFactory

from caminae.core.factories import PathFactory
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
        path = PathFactory.create()
        return {
            'physical_type': PhysicalTypeFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }


class LandEdgeViewsTest(MapEntityTest):
    model = LandEdge
    modelfactory = LandEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'land_type': LandTypeFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }


class CompetenceEdgeViewsTest(MapEntityTest):
    model = CompetenceEdge
    modelfactory = CompetenceEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }


class WorkManagementEdgeViewsTest(MapEntityTest):
    model = WorkManagementEdge
    modelfactory = WorkManagementEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }



class SignageManagementEdgeViewsTest(MapEntityTest):
    model = SignageManagementEdge
    modelfactory = SignageManagementEdgeFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'organization': OrganismFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }
