from django.contrib.gis.geos import LineString, Point
from django.test import TestCase

from geotrek.core.tests.factories import TopologyFactory
from geotrek.maintenance.tests.factories import InterventionFactory, ProjectFactory


class GeometryTriggersTest(TestCase):
    def test_intervention_geom_from_topology(self):
        # Create a topology with a specific geometry
        geom = LineString((0, 0), (1, 1), srid=2154)
        topology = TopologyFactory.create(geom=geom)

        # Create an intervention on this topology
        intervention = InterventionFactory.create(target=topology)

        # Check that intervention.geom has been updated by the trigger
        # We need to refresh from DB because the trigger happened in SQL
        intervention.refresh_from_db()
        self.assertIsNotNone(intervention.geom)
        self.assertEqual(intervention.geom.ewkt, geom.ewkt)

    def test_intervention_geom_update_from_topology(self):
        # Create an intervention on a topology
        geom1 = LineString((0, 0), (1, 1), srid=2154)
        topology = TopologyFactory.create(geom=geom1)
        intervention = InterventionFactory.create(target=topology)

        # Update topology geometry
        geom2 = LineString((0, 0), (2, 2), srid=2154)
        topology.geom = geom2
        topology.save()

        # Check that intervention.geom has been updated
        intervention.refresh_from_db()
        self.assertEqual(intervention.geom.ewkt, geom2.ewkt)

    def test_project_geom_from_interventions(self):
        # Create two interventions with geometries
        geom1 = Point(0, 0, srid=2154)
        topo1 = TopologyFactory.create(geom=geom1)
        inter1 = InterventionFactory.create(target=topo1)

        geom2 = Point(1, 1, srid=2154)
        topo2 = TopologyFactory.create(geom=geom2)
        inter2 = InterventionFactory.create(target=topo2)

        # Create a project and associate interventions
        project = ProjectFactory.create()
        inter1.project = project
        inter1.save()
        inter2.project = project
        inter2.save()

        # Check project geometry
        project.refresh_from_db()
        self.assertIsNotNone(project.geom)
        # ST_Collect(Point(0,0), Point(1,1)) -> MULTIPOINT((0 0), (1 1)) or GEOMETRYCOLLECTION
        # The result depends on ST_Collect behavior and geometries
        self.assertEqual(project.geom.num_geom, 2)

    def test_project_geom_update_on_intervention_change(self):
        # Create a project with one intervention
        project = ProjectFactory.create()
        geom1 = Point(0, 0, srid=2154)
        topo1 = TopologyFactory.create(geom=geom1)
        inter1 = InterventionFactory.create(target=topo1, project=project)

        project.refresh_from_db()
        self.assertEqual(project.geom.num_geom, 1)

        # Add another intervention
        geom2 = Point(1, 1, srid=2154)
        topo2 = TopologyFactory.create(geom=geom2)
        InterventionFactory.create(target=topo2, project=project)

        project.refresh_from_db()
        self.assertEqual(project.geom.num_geom, 2)

        # Remove first intervention from project
        inter1.project = None
        inter1.save()

        project.refresh_from_db()
        self.assertEqual(project.geom.num_geom, 1)
        self.assertEqual(project.geom[0].ewkt, geom2.ewkt)
