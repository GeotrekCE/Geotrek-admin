from django.test import TestCase
from caminae.mapentity.tests import MapEntityTest
from caminae.authent.models import default_structure
from caminae.authent.factories import PathManagerFactory
from caminae.core.factories import StakeFactory
from caminae.common.factories import OrganismFactory

from caminae.maintenance.models import Intervention, InterventionStatus, Project
from caminae.core.factories import (PathFactory, PathAggregationFactory,
                                   TopologyMixinFactory)
from caminae.infrastructure.factories import InfrastructureFactory, SignageFactory
from caminae.maintenance.factories import (InterventionFactory, 
    InterventionDisorderFactory, InterventionStatusFactory,
    ProjectFactory, ContractorFactory)


class InterventionViewsTest(MapEntityTest):
    model = Intervention
    modelfactory = InterventionFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        InterventionStatusFactory.create()  # in case not any in db
        path = PathFactory.create()
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
            'status': InterventionStatus.objects.all()[0].pk,
            'heliport_cost': 0.0,
            'material_cost': 0.0,
            'topology': '{"paths": [%s]}' % path.pk,
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

class InterventionTest(TestCase):
    def test_helpers(self):
        infra = InfrastructureFactory.create()
        sign = SignageFactory.create()
        interv = InterventionFactory.create()
        proj = ProjectFactory.create()

        interv.set_infrastructure(infra)
        self.assertTrue(interv.on_infrastructure())
        self.assertFalse(interv.is_signage())
        self.assertTrue(interv.is_infrastructure())
        self.assertEquals(interv.signages, [])
        self.assertEquals(interv.infrastructures, [infra])

        interv.set_infrastructure(sign)
        self.assertTrue(interv.on_infrastructure())
        self.assertTrue(interv.is_signage())
        self.assertFalse(interv.is_infrastructure())
        self.assertEquals(interv.signages, [sign])
        self.assertEquals(interv.infrastructures, [])

        self.assertFalse(interv.in_project())
        interv.project = proj
        self.assertTrue(interv.in_project())

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

        t = TopologyMixinFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1)
        i3.topology = t

        proj = ProjectFactory.create()
        self.assertEquals(proj.paths, [])
        self.assertEquals(proj.signages, [])
        self.assertEquals(proj.infrastructures, [])

        proj.intervention_set.add(i1)
        self.assertEquals(proj.paths, [p1])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [])

        proj.intervention_set.add(i2)
        self.assertItemsEqual(proj.paths, [p1, p2])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])

        proj.intervention_set.add(i3)
        self.assertEquals(proj.paths, [p1, p2])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])
