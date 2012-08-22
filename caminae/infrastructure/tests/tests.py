from caminae.mapentity.tests import MapEntityTest
from caminae.authent.models import default_structure
from caminae.authent.factories import PathManagerFactory

from caminae.infrastructure.models import Infrastructure, Signage, INFRASTRUCTURE_TYPES
from caminae.core.factories import PathFactory
from caminae.infrastructure.factories import (SignageFactory, 
    InfrastructureFactory, InfrastructureTypeFactory)


class InfrastructureViewsTest(MapEntityTest):
    model = Infrastructure
    modelfactory = InfrastructureFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'name': 'test',
            'description': 'oh',
            'structure': default_structure().pk,
            'type': InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING).pk,
            'geom': '{"paths": [%s]}' % path.pk,
        }


class SignageViewsTest(InfrastructureViewsTest):
    model = Signage
    modelfactory = SignageFactory

    def get_good_data(self):
        data = super(SignageViewsTest, self).get_good_data()
        data['type'] = InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.SIGNAGE).pk
        return data
