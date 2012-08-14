from caminae.mapentity.tests import MapEntityTest
from caminae.authent.models import default_structure
from caminae.authent.factories import PathManagerFactory
from caminae.core.factories import StakeFactory
from caminae.common.factories import OrganismFactory

from caminae.maintenance.models import Intervention, Project
from caminae.maintenance.factories import (InterventionFactory, 
    InterventionDisorderFactory, InterventionStatusFactory,
    ProjectFactory, ContractorFactory)


class InterventionViewsTest(MapEntityTest):
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


class ProjectViewsTest(MapEntityTest):
    model = Project
    modelfactory = ProjectFactory
    userfactory = PathManagerFactory


    def get_bad_data(self):
        return {'begin_year':''}, u'Ce champ est obligatoire.'

    def get_good_data(self):
        return {
            'name': 'test',
            'structure': default_structure().pk,
            'stake': '',
            'begin_year': '2010',
            'end_year': '2012',
            'constraints': '',
            'cost': '12',
            'comments': '',
            'contractors':  ContractorFactory.create().pk,
            'project_owner': OrganismFactory.create().pk,
            'project_manager': OrganismFactory.create().pk,
        }
