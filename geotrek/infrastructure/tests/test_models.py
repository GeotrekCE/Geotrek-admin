from django.conf import settings
from django.test import TestCase

from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.tests.factories import InfrastructureFactory


class InfrastructureTest(TestCase):
    def test_helpers(self):
        p = PathFactory.create()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create(paths=[p])
        else:
            infra = InfrastructureFactory.create(geom=p.geom)

        self.assertCountEqual(p.infrastructures, [infra])
