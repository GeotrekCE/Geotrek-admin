from django.test import TestCase

from caminae.infrastructure.factories import InfrastructureFactory, SignageFactory
from caminae.maintenance.factories import InterventionFactory
from caminae.core.factories import PathFactory, StakeFactory


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
        self.assertTrue(lowstake < highstake)
        
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
