from django.test import TestCase

from caminae.infrastructure.factories import InfrastructureFactory, SignageFactory
from caminae.maintenance.models import Intervention
from caminae.maintenance.factories import InterventionFactory, ProjectFactory
from caminae.core.factories import PathFactory, TopologyFactory, TrailFactory, StakeFactory


class InterventionTest(TestCase):
    def test_infrastructure(self):
        i = InterventionFactory.create()
        self.assertFalse(i.on_infrastructure)
        infra = InfrastructureFactory.create()
        i.set_infrastructure(infra)
        self.assertTrue(i.on_infrastructure)
        sign = SignageFactory.create()
        i.set_infrastructure(sign)
        self.assertTrue(i.on_infrastructure)

    def test_default_stake(self):
        i = InterventionFactory.create()
        i.stake = None
        self.assertTrue(i.stake is None)
        i.save()
        self.assertTrue(i.stake is None)
        
        lowstake = StakeFactory.create()
        highstake = StakeFactory.create()
        if lowstake > highstake:
            tmp = lowstake
            lowstake = highstake
            highstake = tmp
        
        # Add paths to topology
        infra = InfrastructureFactory.create(no_path=True)
        infra.add_path(PathFactory.create(stake=lowstake))
        infra.add_path(PathFactory.create(stake=highstake))
        infra.add_path(PathFactory.create(stake=lowstake))
        i.set_infrastructure(infra)
        # Stake is not None anymore
        i.save()
        self.assertFalse(i.stake is None)
        # Make sure it took higher stake
        self.assertEqual(i.stake, highstake)

    def test_path_helpers(self):
        p = PathFactory.create()

        self.assertEquals(len(p.interventions), 0)
        self.assertEquals(len(p.projects), 0)

        sign = SignageFactory.create(no_path=True)
        sign.add_path(p, start=0.5, end=0.5)

        infra = InfrastructureFactory.create(no_path=True)
        infra.add_path(p)

        i1 = InterventionFactory.create()
        i1.set_infrastructure(sign)
        i1.save()

        self.assertItemsEqual(p.interventions, [i1])

        i2 = InterventionFactory.create()
        i2.set_infrastructure(infra)
        i2.save()

        self.assertItemsEqual(p.interventions, [i1, i2])

        proj = ProjectFactory.create()
        proj.interventions.add(i1)
        proj.interventions.add(i2)

        self.assertItemsEqual(p.projects, [proj])

    def test_trail_helpers(self):
        t = TrailFactory.create()
        self.assertEqual(0, len(t.interventions))
        
        p = PathFactory.create()
        t.paths.add(p)
        
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p)
        i = InterventionFactory(topology=topo)
        self.assertEqual(1, len(t.interventions))
        self.assertEqual([i], t.interventions)

    def test_helpers(self):
        infra = InfrastructureFactory.create()
        sign = SignageFactory.create()
        interv = InterventionFactory.create()
        proj = ProjectFactory.create()

        self.assertFalse(interv.on_infrastructure)
        self.assertEquals(interv.infrastructure, None)

        interv.set_infrastructure(infra)
        self.assertTrue(interv.on_infrastructure)
        self.assertFalse(interv.is_signage())
        self.assertTrue(interv.is_infrastructure())
        self.assertEquals(interv.signages, [])
        self.assertEquals(interv.infrastructures, [infra])
        self.assertEquals(interv.infrastructure, infra)

        interv.set_infrastructure(sign)
        self.assertTrue(interv.on_infrastructure())
        self.assertTrue(interv.is_signage())
        self.assertFalse(interv.is_infrastructure())
        self.assertEquals(interv.signages, [sign])
        self.assertEquals(interv.infrastructures, [])
        self.assertEquals(interv.infrastructure, sign)

        self.assertFalse(interv.in_project())
        interv.project = proj
        self.assertTrue(interv.in_project())

    def test_delete_topology(self):
        infra = InfrastructureFactory.create()
        interv = InterventionFactory.create()
        interv.set_infrastructure(infra)
        infra.delete()
        self.assertEqual(Intervention.objects.existing().count(), 0)

