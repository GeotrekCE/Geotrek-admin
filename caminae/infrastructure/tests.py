from caminae.mapentity.tests import MapEntityTest
from caminae.authent.models import default_structure
from caminae.authent.factories import PathManagerFactory

from caminae.infrastructure.models import Infrastructure, Signage
from caminae.infrastructure.factories import (SignageFactory, 
    InfrastructureFactory, InfrastructureTypeFactory)


class InfrastructureViewsTest(MapEntityTest):
    model = Infrastructure
    modelfactory = InfrastructureFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        return {
            'name': 'test',
            'description': 'oh',
            'structure': default_structure().pk,
            'type': InfrastructureTypeFactory.create().pk,
            'geom': 'POINT (0.0 0.0 0.0)',
        }


class SignageViewsTest(InfrastructureViewsTest):
    model = Signage
    modelfactory = SignageFactory
