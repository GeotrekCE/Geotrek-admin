from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import LineString, Polygon, MultiPolygon
from django.core.urlresolvers import reverse

from caminae.mapentity.tests import MapEntityTest
from caminae.authent.factories import PathManagerFactory

from caminae.core.factories import PathFactory
from caminae.common.factories import OrganismFactory
from caminae.land.models import (PhysicalEdge, LandEdge, CompetenceEdge,
    WorkManagementEdge, SignageManagementEdge, City)
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

class CouchesSIGTest(TestCase):

    def test_views_status(self):
        for layer in ['city', 'restrictedarea', 'district']:
            url = reverse('land:%s_layer' % layer)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        
        url = reverse('land:district_json_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_troncons_link(self):
        p1 = PathFactory.create(geom=LineString((0,0,0), (1,1,1)))
        p2 = PathFactory.create(geom=LineString((1,1,1), (3,3,3)))
        p3 = PathFactory.create(geom=LineString((3,3,3), (4,4,4)))

        # Paths should not be linked to anything at this stage
        self.assertEquals(p1.aggregations.count(), 0)
        self.assertEquals(p2.aggregations.count(), 0)
        self.assertEquals(p3.aggregations.count(), 0)

        c1 = City.objects.create(code='005177', name='Trifouillis-les-oies',
                 geom=MultiPolygon(Polygon(((0,0), (2,0), (2,4), (0,4), (0,0)),
                              srid=settings.SRID)))
        c2 = City.objects.create(code='005179', name='Trifouillis-les-poules',
                 geom=MultiPolygon(Polygon(((2,0), (5,0), (5,4), (2,4), (2,0)),
                              srid=settings.SRID)))

        # There should be automatic link after insert
        self.assertEquals(p1.aggregations.count(), 1)
        self.assertEquals(p2.aggregations.count(), 2)
        self.assertEquals(p3.aggregations.count(), 1)

        c1.geom = MultiPolygon(Polygon(((1.5,0), (2,0), (2,4), (1.5,4), (1.5,0)),
                                       srid=settings.SRID))
        c1.save()

        # Links should have been updated after geom update
        self.assertEquals(p1.aggregations.count(), 0)
        self.assertEquals(p2.aggregations.count(), 2)
        self.assertEquals(p3.aggregations.count(), 1)

        c1.delete()

        # Links should have been updated after delete
        self.assertEquals(p1.aggregations.count(), 0)
        self.assertEquals(p2.aggregations.count(), 1)
        self.assertEquals(p3.aggregations.count(), 1)
