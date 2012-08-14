from caminae.mapentity.tests import MapEntityTest
from caminae.authent.models import default_structure
from caminae.authent.factories import PathManagerFactory
from caminae.maintenance.factories import InterventionFactory

from caminae.core.factories import StakeFactory
from caminae.maintenance.models import Intervention
from caminae.maintenance.factories import InterventionDisorderFactory, InterventionStatusFactory


class ViewsTest(MapEntityTest):
    model = Intervention
    modelfactory = InterventionFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        return {
            'name': 'test',
            'structure': default_structure().pk,
            'stake': '',
            'disorders': InterventionDisorderFactory.create().pk,
            'comments': '',
            'slope': 0,
            'area': 0,
            'subcontract_cost': 0.0,
            'stake': StakeFactory.create().pk,
            'height': 0.0,
            'project': '',
            'width': 0.0,
            'length': 0.0,
            'status': InterventionStatusFactory.create().pk,
            'heliport_cost': 0.0,
            'material_cost': 0.0,
            'geom': 'POINT (0.0 0.0 0.0)',
        }
