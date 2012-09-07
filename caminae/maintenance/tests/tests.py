from collections import OrderedDict

from django.test import TestCase
from django.utils import simplejson

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
            'date': '2012-08-23',
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

    def test_form_on_infrastructure(self):
        user = self.userfactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)
        
        infra = InfrastructureFactory.create()
        infrastr = u"%s" % infra
        # For creation
        response = self.client.get(Intervention.get_add_url() + '?infrastructure=%s' % infra.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, infrastr)
        # For edition
        intervention = InterventionFactory.create()
        intervention.set_infrastructure(infra)
        response = self.client.get(infra.get_update_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, infrastr)


class ProjectViewsTest(MapEntityTest):
    model = Project
    modelfactory = ProjectFactory
    userfactory = PathManagerFactory


    def get_bad_data(self):
        return OrderedDict([
                ('begin_year', ''),
                ('funding_set-TOTAL_FORMS', '0'),
                ('funding_set-INITIAL_FORMS', '1'),
                ('funding_set-MAX_NUM_FORMS', '0'),
            ]), u'Ce champ est obligatoire.'

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
            
            'funding_set-TOTAL_FORMS': '2',
            'funding_set-INITIAL_FORMS': '0',
            'funding_set-MAX_NUM_FORMS': '',
            
            'funding_set-0-amount': '468.0',
            'funding_set-0-organism': OrganismFactory.create().pk,
            'funding_set-0-project': '',
            'funding_set-0-id': '',
            'funding_set-0-DELETE': '',

            'funding_set-1-amount': '789',
            'funding_set-1-organism': OrganismFactory.create().pk,
            'funding_set-1-project': '',
            'funding_set-1-id': '',
            'funding_set-1-DELETE': ''
        }

    def test_project_layer(self):
        p1 = ProjectFactory.create()
        ProjectFactory.create()
        InterventionFactory.create(project=p1)
        
        # Check that only p1 is in geojson
        response = self.client.get(self.model.get_layer_url())
        self.assertEqual(response.status_code, 200)
        geojson = simplejson.loads(response.content)
        features = geojson['features']
        
        self.assertEqual(len(Project.objects.all()), 2)
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]['properties']['pk'], p1.pk)

    def test_project_bbox_filter(self):
        p1 = ProjectFactory.create()
        ProjectFactory.create()
        ProjectFactory.create()
        
        t = TopologyMixinFactory.create()
        InterventionFactory.create(project=p1, topology=t)
        
        def jsonlist(bbox):
            url = self.model.get_jsonlist_url() + bbox
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            json = simplejson.loads(response.content)
            return json['aaData']
        
        # Check that projects without interventions are always present
        self.assertEqual(len(Project.objects.all()), 3)
        self.assertEqual(len(jsonlist('')), 3)
        self.assertEqual(len(jsonlist('?bbox=POLYGON((1%202%200%2C1%202%200%2C1%202%200%2C1%202%200%2C1%202%200))')), 2)


class InterventionTest(TestCase):
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

        proj.interventions.add(i1)
        self.assertEquals(proj.paths, [p1])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [])

        proj.interventions.add(i2)
        self.assertItemsEqual(proj.paths, [p1, p2])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])

        proj.interventions.add(i3)
        self.assertItemsEqual(proj.paths, [p1, p2])
        self.assertEquals(proj.signages, [sign])
        self.assertEquals(proj.infrastructures, [infra])
