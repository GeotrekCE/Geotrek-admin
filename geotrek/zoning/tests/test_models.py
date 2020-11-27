from unittest import skipIf
from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import LineString, Polygon, MultiPolygon

from geotrek.core.models import Topology
from geotrek.core.factories import PathFactory
from geotrek.land.tests.test_views import EdgeHelperTest
from geotrek.signage.factories import SignageFactory
from geotrek.zoning.models import City
from geotrek.zoning.factories import (DistrictEdgeFactory, CityEdgeFactory, CityFactory, DistrictFactory,
                                      RestrictedAreaFactory, RestrictedAreaTypeFactory, RestrictedAreaEdgeFactory)


class CitiesEdgeTest(EdgeHelperTest):

    factory = CityEdgeFactory
    helper_name = 'city_edges'


class RestrictedAreaEdgeTest(EdgeHelperTest):

    factory = RestrictedAreaEdgeFactory
    helper_name = 'area_edges'


class DistrictEdgeTest(EdgeHelperTest):

    factory = DistrictEdgeFactory
    helper_name = 'district_edges'


class PathUpdateTest(TestCase):

    def test_path_touching_land_layer(self):
        p1 = PathFactory.create(geom=LineString((3, 3), (4, 4), srid=settings.SRID))
        City.objects.create(code='005177', name='Trifouillis-les-oies',
                            geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)),
                                                      srid=settings.SRID)))
        p1.geom = LineString((2, 2), (4, 4), srid=settings.SRID)
        p1.save()


class ZoningLayersUpdateTest(TestCase):

    def test_paths_link(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (1, 1)))
        p2 = PathFactory.create(geom=LineString((1, 1), (3, 3)))
        p3 = PathFactory.create(geom=LineString((3, 3), (4, 4)))
        p4 = PathFactory.create(geom=LineString((4, 1), (6, 2), (4, 3)))

        # Paths should not be linked to anything at this stage
        self.assertEqual(p1.aggregations.count(), 0)
        self.assertEqual(p2.aggregations.count(), 0)
        self.assertEqual(p3.aggregations.count(), 0)

        c1 = City.objects.create(
            code='005177',
            name='Trifouillis-les-oies',
            geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 4), (0, 4), (0, 0)),
                              srid=settings.SRID)))
        City.objects.create(
            code='005179',
            name='Trifouillis-les-poules',
            geom=MultiPolygon(Polygon(((2, 0), (5, 0), (5, 4), (2, 4), (2, 0)),
                              srid=settings.SRID)))

        # There should be automatic link after insert
        self.assertEqual(p1.aggregations.count(), 1)
        self.assertEqual(p2.aggregations.count(), 2)
        self.assertEqual(p3.aggregations.count(), 1)
        self.assertEqual(p4.aggregations.count(), 2)

        c1.geom = MultiPolygon(Polygon(((1.5, 0), (2, 0), (2, 4), (1.5, 4), (1.5, 0)),
                                       srid=settings.SRID))
        c1.save()

        # Links should have been updated after geom update
        self.assertEqual(p1.aggregations.count(), 0)
        self.assertEqual(p2.aggregations.count(), 2)
        self.assertEqual(p3.aggregations.count(), 1)
        self.assertEqual(p4.aggregations.count(), 2)

        c1.delete()

        # Links should have been updated after delete
        self.assertEqual(p1.aggregations.count(), 0)
        self.assertEqual(p2.aggregations.count(), 1)
        self.assertEqual(p3.aggregations.count(), 1)
        self.assertEqual(p4.aggregations.count(), 2)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_city_with_path_ends_on_border(self):
        """
                 |    |
                 |p1  |p2
                 |    |
        +--------+----+---+
        |                 |
        |                 | City
        |                 |
        +-----------------+
        """
        # Create a path before city to test one trigger
        p1 = PathFactory(geom=LineString((1, 1), (1, 2)))
        p1.save()
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)),
                                           srid=settings.SRID)))
        c.save()
        # Create a path after city to the the another trigger
        p2 = PathFactory(geom=LineString((1.5, 2), (1.5, 1)))
        p2.save()
        self.assertEqual(p1.city_edges.count(), 0)
        self.assertEqual(p2.city_edges.count(), 0)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_city_with_topo(self):
        """
        +-----------------+
        |        S        |
        |    +---x---+    |
        |    |       |    | City
        |    |p      |    |
        |    O       O    |
        |                 |
        +-----------------+
        """
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)),
                                           srid=settings.SRID)))
        c.save()
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)))
        p.save()
        signage = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        self.assertEqual(signage.city_edges.count(), 1)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_city_with_topo_2(self):
        """
                 S
             +---x---+
         _ _ | _ _ _ | _ _
        |    |p      |    |
        |    O       O    | City
        |                 |
        +-----------------+
        """
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)),
                                           srid=settings.SRID)))
        c.save()
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)))
        p.save()
        signage = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        self.assertEqual(signage.city_edges.count(), 0)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_city_with_topo_3(self):
        """
             +-------+
         _ _ | _ _ _ | _ _
        |    |p      |    |
        |    O       X S  | City
        |                 |
        +-----------------+
        """
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)),
                                           srid=settings.SRID)))
        c.save()
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)))
        p.save()
        signage = SignageFactory.create(paths=[(p, 1, 1)])
        self.assertEqual(signage.city_edges.count(), 1)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_city_with_topo_on_loop(self):
        """
        +-----------------+
        |            S    |
        |    +-------x    |
        |    |       |    | City
        |    |p      |    |
        |    O-------+    |
        |                 |
        +-----------------+
        """
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)),
                                           srid=settings.SRID)))
        c.save()
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)))
        p.save()
        signage = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        self.assertEqual(signage.city_edges.count(), 1)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_city_with_topo_on_loop_2(self):
        """
                     S
             +-------x
         _ _ | _ _ _ | _ _
        |    |p      |    |
        |    O-------+    | City
        |                 |
        +-----------------+
        """
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)),
                                           srid=settings.SRID)))
        c.save()
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)))
        p.save()
        signage = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        self.assertEqual(signage.city_edges.count(), 0)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_city_with_topo_on_loop_3(self):
        """

             +-------+
         _ _ | _ _ _ | _ _
        |    |p      |    |
        |    O-------x S  | City
        |                 |
        +-----------------+
        """
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)),
                                           srid=settings.SRID)))
        c.save()
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)))
        p.save()
        signage = SignageFactory.create(paths=[(p, 0.75, 0.75)])
        self.assertEqual(signage.city_edges.count(), 1)

    def test_couches_sig_link(self):
        """
        +-----------------+    -
        |                 |ra2  |
        |    +-------+    |     |
        | _ _|  _ _ _|_ _ |      - C
        |    |p      |    |     |
        |    O       O    |     |
        |                 |ra1  |
        +-----------------+    -
        """
        # Fake restricted areas
        ra1 = RestrictedAreaFactory.create(geom=MultiPolygon(
            Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)))))
        ra2 = RestrictedAreaFactory.create(geom=MultiPolygon(
            Polygon(((0, 1), (2, 1), (2, 2), (0, 2), (0, 1)))))

        # Fake city
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)),
                                   srid=settings.SRID)))
        c.save()

        # Fake paths in these areas
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)))
        p.save()

        # This should results in 3 PathAggregation (2 for RA1, 1 for RA2, 1 for City)
        self.assertEqual(p.aggregations.count(), 4)
        self.assertEqual(p.topology_set.count(), 4)

        # PathAgg is plain for City
        t_c = c.cityedge_set.get().topo_object
        pa = c.cityedge_set.get().aggregations.get()
        self.assertEqual(pa.start_position, 0.0)
        self.assertEqual(pa.end_position, 1.0)

        # PathAgg is splitted for RA
        self.assertEqual(ra1.restrictedareaedge_set.count(), 2)
        self.assertEqual(ra2.restrictedareaedge_set.count(), 1)
        rae1a = ra1.restrictedareaedge_set.filter(aggregations__start_position=0).get()
        rae1b = ra1.restrictedareaedge_set.filter(aggregations__end_position=1).get()
        pa1a = rae1a.aggregations.get()
        pa1b = rae1b.aggregations.get()
        t_ra1a = rae1a.topo_object
        t_ra1b = rae1b.topo_object
        pa2 = ra2.restrictedareaedge_set.get().aggregations.get()
        t_ra2 = ra2.restrictedareaedge_set.get().topo_object
        self.assertAlmostEqual(pa1a.start_position, 0.0)
        self.assertAlmostEqual(pa1a.end_position, 0.5 / 3)
        self.assertAlmostEqual(pa1b.start_position, 2.5 / 3)
        self.assertAlmostEqual(pa1b.end_position, 1.0)
        self.assertAlmostEqual(pa2.start_position, 0.5 / 3)
        self.assertAlmostEqual(pa2.end_position, 2.5 / 3)

        # Ensure everything is in order after update
        p.geom = LineString((0.5, 0.5), (1.5, 0.5))
        p.save()
        self.assertEqual(p.aggregations.count(), 2)
        self.assertEqual(p.topology_set.count(), 2)
        # Topology are re-created at DB-level after any update
        self.assertRaises(Topology.DoesNotExist,
                          Topology.objects.get, pk=t_c.pk)
        self.assertRaises(Topology.DoesNotExist,
                          Topology.objects.get, pk=t_ra1a.pk)
        self.assertRaises(Topology.DoesNotExist,
                          Topology.objects.get, pk=t_ra1b.pk)
        self.assertRaises(Topology.DoesNotExist,
                          Topology.objects.get, pk=t_ra2.pk)
        self.assertEqual(ra1.restrictedareaedge_set.count(), 1)
        # a new association exists for C
        t_c = c.cityedge_set.get().topo_object
        self.assertEqual(Topology.objects.filter(pk=t_c.pk).count(), 1)
        # a new association exists for RA1
        t_ra1 = ra1.restrictedareaedge_set.get().topo_object
        self.assertEqual(Topology.objects.filter(pk=t_ra1.pk).count(), 1)
        pa1 = ra1.restrictedareaedge_set.get().aggregations.get()
        self.assertEqual(pa1.start_position, 0.0)
        self.assertEqual(pa1.end_position, 1.0)
        # RA2 is not connected anymore
        self.assertEqual(ra2.restrictedareaedge_set.count(), 0)
        self.assertEqual(Topology.objects.filter(pk=t_ra2.pk).count(), 0)

        # All intermediary objects should be cleaned on delete
        p.delete()
        self.assertEqual(c.cityedge_set.count(), 0)
        self.assertEqual(Topology.objects.filter(pk=t_c.pk).count(), 0)
        self.assertEqual(ra1.restrictedareaedge_set.count(), 0)
        self.assertEqual(Topology.objects.filter(pk=t_ra1.pk).count(), 0)
        self.assertEqual(ra2.restrictedareaedge_set.count(), 0)
        self.assertEqual(Topology.objects.filter(pk=t_ra2.pk).count(), 0)

    def test_couches_sig_link_path_loop(self):
        """
        +-----------------+    -
        |                 |ra2  |
        |    +-------+    |     |
        | _ _|  _ _ _|_ _ |      - C
        |    |p      |    |     |
        |    O-------+    |     |
        |                 |ra1  |
        +-----------------+    -
        """
        # Fake restricted areas
        ra1 = RestrictedAreaFactory.create(geom=MultiPolygon(
            Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)))))
        ra2 = RestrictedAreaFactory.create(geom=MultiPolygon(
            Polygon(((0, 1), (2, 1), (2, 2), (0, 2), (0, 1)))))

        # Fake city
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)),
                                           srid=settings.SRID)))
        c.save()

        # Fake paths in these areas
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)))
        p.save()

        # This should results in 3 PathAggregation (2 for RA1, 1 for RA2, 1 for City)
        self.assertEqual(p.aggregations.count(), 4)
        self.assertEqual(p.topology_set.count(), 4)

        # PathAgg is plain for City
        t_c = c.cityedge_set.get().topo_object
        pa = c.cityedge_set.get().aggregations.get()
        self.assertEqual(pa.start_position, 0.0)
        self.assertEqual(pa.end_position, 1.0)

        # PathAgg is splitted for RA
        self.assertEqual(ra1.restrictedareaedge_set.count(), 2)
        self.assertEqual(ra2.restrictedareaedge_set.count(), 1)
        rae1a = ra1.restrictedareaedge_set.filter(aggregations__start_position=0).get()
        rae1b = ra1.restrictedareaedge_set.filter(aggregations__end_position=1).get()
        pa1a = rae1a.aggregations.get()
        pa1b = rae1b.aggregations.get()
        t_ra1a = rae1a.topo_object
        t_ra1b = rae1b.topo_object
        pa2 = ra2.restrictedareaedge_set.get().aggregations.get()
        t_ra2 = ra2.restrictedareaedge_set.get().topo_object
        self.assertAlmostEqual(pa1a.start_position, 0.0)
        self.assertAlmostEqual(pa1a.end_position, 0.125)
        self.assertAlmostEqual(pa1b.start_position, 0.625)
        self.assertAlmostEqual(pa1b.end_position, 1.0)
        self.assertAlmostEqual(pa2.start_position, 0.125)
        self.assertAlmostEqual(pa2.end_position, 0.625)

        # Ensure everything is in order after update
        p.geom = LineString((0.5, 0.5), (1.5, 0.5))
        p.save()
        self.assertEqual(p.aggregations.count(), 2)
        self.assertEqual(p.topology_set.count(), 2)
        # Topology are re-created at DB-level after any update
        self.assertRaises(Topology.DoesNotExist,
                          Topology.objects.get, pk=t_c.pk)
        self.assertRaises(Topology.DoesNotExist,
                          Topology.objects.get, pk=t_ra1a.pk)
        self.assertRaises(Topology.DoesNotExist,
                          Topology.objects.get, pk=t_ra1b.pk)
        self.assertRaises(Topology.DoesNotExist,
                          Topology.objects.get, pk=t_ra2.pk)
        self.assertEqual(ra1.restrictedareaedge_set.count(), 1)
        # a new association exists for C
        t_c = c.cityedge_set.get().topo_object
        self.assertEqual(Topology.objects.filter(pk=t_c.pk).count(), 1)
        # a new association exists for RA1
        t_ra1 = ra1.restrictedareaedge_set.get().topo_object
        self.assertEqual(Topology.objects.filter(pk=t_ra1.pk).count(), 1)
        pa1 = ra1.restrictedareaedge_set.get().aggregations.get()
        self.assertEqual(pa1.start_position, 0.0)
        self.assertEqual(pa1.end_position, 1.0)
        # RA2 is not connected anymore
        self.assertEqual(ra2.restrictedareaedge_set.count(), 0)
        self.assertEqual(Topology.objects.filter(pk=t_ra2.pk).count(), 0)

        # All intermediary objects should be cleaned on delete
        p.delete()
        self.assertEqual(c.cityedge_set.count(), 0)
        self.assertEqual(Topology.objects.filter(pk=t_c.pk).count(), 0)
        self.assertEqual(ra1.restrictedareaedge_set.count(), 0)
        self.assertEqual(Topology.objects.filter(pk=t_ra1.pk).count(), 0)
        self.assertEqual(ra2.restrictedareaedge_set.count(), 0)
        self.assertEqual(Topology.objects.filter(pk=t_ra2.pk).count(), 0)


class ZoningModelsTest(TestCase):
    def test_city(self):
        city = CityFactory.create(name="Are", code='09000',
                                  geom=MultiPolygon(Polygon(((200, 0), (300, 0), (300, 100), (200, 100), (200, 0)),
                                                            srid=settings.SRID)))
        self.assertEqual(str(city), "Are")

    def test_city_edge(self):
        city_edge = CityEdgeFactory()
        self.assertEqual(str(city_edge), "City edge: {}".format(city_edge.city.name))

    def test_district(self):
        district = DistrictFactory.create(name="Lil",
                                          geom=MultiPolygon(Polygon(((201, 0), (300, 0), (300, 100), (200, 100), (201, 0)),
                                                                    srid=settings.SRID)))
        self.assertEqual(str(district), "Lil")

    def test_district_edge(self):
        district_edge = DistrictEdgeFactory()
        self.assertEqual(str(district_edge), "District edge: {}".format(district_edge.district.name))

    def test_restricted_area(self):
        area_type = RestrictedAreaTypeFactory.create(name="Test")
        restricted_area = RestrictedAreaFactory.create(area_type=area_type, name="Tel",
                                                       geom=MultiPolygon(Polygon(((201, 0), (300, 0), (300, 100), (200, 100), (201, 0)),
                                                                                 srid=settings.SRID)))
        self.assertEqual(str(restricted_area), "Test - Tel")

    def test_restricted_area_edge(self):
        restricted_area_edge = RestrictedAreaEdgeFactory()
        self.assertEqual(str(restricted_area_edge), "Restricted area edge: {} - {}".format(restricted_area_edge.restricted_area.area_type,
                                                                                           restricted_area_edge.restricted_area.name))
