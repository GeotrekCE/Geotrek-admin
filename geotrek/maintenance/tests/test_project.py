from django.test import TestCase
from django.conf import settings

from unittest import skipIf

from geotrek.infrastructure.factories import InfrastructureFactory
from geotrek.signage.factories import SignageFactory
from geotrek.maintenance.factories import InterventionFactory, ProjectFactory
from geotrek.core.factories import TopologyFactory, PathAggregationFactory
from geotrek.land.factories import (SignageManagementEdgeFactory, WorkManagementEdgeFactory,
                                    CompetenceEdgeFactory)
from geotrek.zoning.factories import (CityEdgeFactory, DistrictEdgeFactory,
                                      RestrictedAreaEdgeFactory)


class ProjectTest(TestCase):
    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_helpers(self):
        i1 = InterventionFactory.create()
        i2 = InterventionFactory.create()
        i3 = InterventionFactory.create()
        sign = SignageFactory.create()
        i1.set_topology(sign)
        p1 = sign.paths.get()

        infra = InfrastructureFactory.create()
        i2.set_topology(infra)
        p2 = infra.paths.get()

        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1)
        i3.topology = t

        proj = ProjectFactory.create()
        self.assertItemsEqual(proj.paths.all(), [])
        self.assertEquals(proj.signages, [])
        self.assertEquals(proj.infrastructures, [])

        i1.save()

        proj.interventions.add(i1)
        self.assertItemsEqual(proj.paths.all(), [p1])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [])

        i2.save()

        proj.interventions.add(i2)
        self.assertItemsEqual(proj.paths.all(), [p1, p2])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])

        i3.save()

        proj.interventions.add(i3)
        self.assertItemsEqual(proj.paths.all(), [p1, p2])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_helpers_nds(self):
        i1 = InterventionFactory.create()
        i2 = InterventionFactory.create()
        i3 = InterventionFactory.create()
        sign = SignageFactory.create(geom="SRID=4326;POINT(0 5)")
        i1.set_topology(sign)

        infra = InfrastructureFactory.create(geom="SRID=4326;POINT(1 5)")
        i2.set_topology(infra)

        t = TopologyFactory.create(geom="SRID=4326;POINT(2 5)")
        i3.topology = t

        proj = ProjectFactory.create()
        self.assertItemsEqual(proj.paths.all(), [])
        self.assertEquals(proj.signages, [])
        self.assertEquals(proj.infrastructures, [])

        i1.save()

        proj.interventions.add(i1)
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [])

        i2.save()

        proj.interventions.add(i2)
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])

        i3.save()

        proj.interventions.add(i3)
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])

    def test_deleted_intervention(self):
        i1 = InterventionFactory.create()
        sign = SignageFactory.create()
        i1.set_topology(sign)
        i1.save()

        proj = ProjectFactory.create()
        proj.interventions.add(i1)
        self.assertEquals(proj.signages, [sign])
        i1.delete()
        self.assertEquals(proj.signages, [])

    def test_deleted_infrastructure(self):
        i1 = InterventionFactory.create()
        infra = InfrastructureFactory.create()
        i1.set_topology(infra)
        i1.save()

        proj = ProjectFactory.create()
        proj.interventions.add(i1)
        self.assertEquals(proj.infrastructures, [infra])

        infra.delete()

        self.assertEquals(proj.infrastructures, [])


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class ProjectLandTest(TestCase):
    def setUp(self):
        self.intervention = InterventionFactory.create()
        self.project = ProjectFactory.create()
        self.project.interventions.add(self.intervention)
        self.project.interventions.add(InterventionFactory.create())

        infra = InfrastructureFactory.create()
        self.intervention.set_topology(infra)
        self.intervention.save()

        path = infra.paths.get()

        self.signagemgt = SignageManagementEdgeFactory.create(no_path=True)
        self.signagemgt.add_path(path, start=0.3, end=0.7)
        self.workmgt = WorkManagementEdgeFactory.create(no_path=True)
        self.workmgt.add_path(path, start=0.3, end=0.7)
        self.competencemgt = CompetenceEdgeFactory.create(no_path=True)
        self.competencemgt.add_path(path, start=0.3, end=0.7)

        self.cityedge = CityEdgeFactory.create(no_path=True)
        self.cityedge.add_path(path, start=0.3, end=0.7)
        self.districtedge = DistrictEdgeFactory.create(no_path=True)
        self.districtedge.add_path(path, start=0.3, end=0.7)
        self.restricted = RestrictedAreaEdgeFactory.create(no_path=True)
        self.restricted.add_path(path, start=0.3, end=0.7)

    def test_project_has_signage_management(self):
        self.assertIn(self.signagemgt, self.intervention.signage_edges)
        self.assertIn(self.signagemgt, self.project.signage_edges)

    def test_project_has_work_management(self):
        self.assertIn(self.workmgt, self.intervention.work_edges)
        self.assertIn(self.workmgt, self.project.work_edges)

    def test_project_has_competence_management(self):
        self.assertIn(self.competencemgt, self.intervention.competence_edges)
        self.assertIn(self.competencemgt, self.project.competence_edges)

    def test_project_has_city_management(self):
        self.assertIn(self.cityedge, self.intervention.city_edges)
        self.assertIn(self.cityedge, self.project.city_edges)
        self.assertIn(self.cityedge.city, self.project.cities)

    def test_project_has_district_management(self):
        self.assertIn(self.districtedge, self.intervention.district_edges)
        self.assertIn(self.districtedge, self.project.district_edges)
        self.assertIn(self.districtedge.district, self.project.districts)

    def test_project_has_restricted_management(self):
        self.assertIn(self.restricted, self.intervention.area_edges)
        self.assertIn(self.restricted, self.project.area_edges)
        self.assertIn(self.restricted.restricted_area, self.project.areas)
