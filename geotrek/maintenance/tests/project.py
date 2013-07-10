from django.test import TestCase

from geotrek.infrastructure.factories import InfrastructureFactory, SignageFactory
from geotrek.maintenance.factories import InterventionFactory, ProjectFactory
from geotrek.core.factories import TopologyFactory, PathAggregationFactory


class ProjectTest(TestCase):
    def test_helpers(self):
        i1 = InterventionFactory.create()
        i2 = InterventionFactory.create()
        i3 = InterventionFactory.create()

        sign = SignageFactory.create()
        i1.set_infrastructure(sign)
        p1 = sign.paths.get()

        infra = InfrastructureFactory.create()
        i2.set_infrastructure(infra)
        p2 = infra.paths.get()

        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1)
        i3.topology = t

        proj = ProjectFactory.create()
        self.assertItemsEqual(proj.paths.all(), [])
        self.assertEquals(proj.signages, [])
        self.assertEquals(proj.infrastructures, [])

        proj.interventions.add(i1)
        self.assertItemsEqual(proj.paths.all(), [p1])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [])

        proj.interventions.add(i2)
        self.assertItemsEqual(proj.paths.all(), [p1, p2])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])

        proj.interventions.add(i3)
        self.assertItemsEqual(proj.paths.all(), [p1, p2])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])

    def test_deleted_intervention(self):
        i1 = InterventionFactory.create()
        sign = SignageFactory.create()
        i1.set_infrastructure(sign)

        proj = ProjectFactory.create()
        proj.interventions.add(i1)
        self.assertEquals(proj.signages, [sign])

        i1.delete()

        self.assertEquals(proj.signages, [])

    def test_deleted_infrastructure(self):
        i1 = InterventionFactory.create()
        infra = InfrastructureFactory.create()
        i1.set_infrastructure(infra)

        proj = ProjectFactory.create()
        proj.interventions.add(i1)
        self.assertEquals(proj.infrastructures, [infra])

        infra.delete()

        self.assertEquals(proj.infrastructures, [])
