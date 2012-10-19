# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.conf import settings
from django.contrib.gis.geos import Point, LineString
from django.contrib.gis import gdal
from django.test import TestCase
from django.utils import simplejson

from caminae.mapentity.tests import MapEntityTest
from caminae.authent.models import default_structure
from caminae.authent.factories import PathManagerFactory
from caminae.core.factories import StakeFactory
from caminae.core.models import TopologyMixin
from caminae.common.factories import OrganismFactory

from caminae.mapentity import shape_exporter

from caminae.maintenance.models import Intervention, InterventionStatus, Project
from caminae.maintenance.views import ProjectFormatList
from caminae.core.factories import (PathFactory, PathAggregationFactory,
                                   TopologyMixinFactory, TrailFactory)
from caminae.infrastructure.factories import InfrastructureFactory, SignageFactory
from caminae.maintenance.factories import (InterventionFactory, 
    InterventionDisorderFactory, InterventionStatusFactory,
    ProjectFactory, ContractorFactory, InterventionJobFactory)


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
            
            'manday_set-TOTAL_FORMS': '2',
            'manday_set-INITIAL_FORMS': '0',
            'manday_set-MAX_NUM_FORMS': '',
            
            'manday_set-0-nb_days': '48.75',
            'manday_set-0-job': InterventionJobFactory.create().pk,
            'manday_set-0-id': '',
            'manday_set-0-DELETE': '',
            
            'manday_set-1-nb_days': '12',
            'manday_set-1-job': InterventionJobFactory.create().pk,
            'manday_set-1-id': '',
            'manday_set-1-DELETE': '',
        }

    def test_form_on_infrastructure(self):
        self.login()
        
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

    def test_form_default_stake(self):
        self.login()
        good_data = self.get_good_data()
        good_data['stake'] = ''
        good_data['topology'] = """
        {"offset":0,"positions":{"0":[0.8298653170816073,1],"2":[0,0.04593024777973237]},"paths":[%s,%s,%s]}
        """ % (PathFactory.create().pk, PathFactory.create().pk, PathFactory.create().pk)
        response = self.client.post(Intervention.get_add_url(), good_data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response._headers['location'][1])
        self.assertTrue('object' in response.context)
        intervention = response.context['object']
        self.assertFalse(intervention.stake is None)


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
            'type': '',
            'domain': '',
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

    def test_path_helpers(self):
        p = PathFactory.create()

        self.assertEquals(len(p.interventions), 0)
        self.assertEquals(len(p.projects), 0)

        sign = SignageFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=sign, path=p,
                                      start_position=0.5, end_position=0.5)

        infra = InfrastructureFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=infra, path=p)

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
        
        topo = TopologyMixinFactory.create(no_path=True)
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


class ExportTest(TestCase):

    def test_shape_mixed(self):
        """
        Test that a project made of intervention of different geom create multiple files.
        Check that those files are each of a different type (Point/LineString) and that
        the project and the intervention are correctly referenced in it.
        """

        # Create topology line
        topo_line = TopologyMixinFactory.create(no_path=True)
        line = PathFactory.create(geom=LineString(Point(10,10,0), Point(11, 10, 0)))
        PathAggregationFactory.create(topo_object=topo_line, path=line)

        # Create a topology point
        lng, lat = tuple(Point(1, 1, srid=settings.SRID).transform(settings.API_SRID, clone=True))

        closest_path = PathFactory(geom=LineString(Point(0, 0, 0), Point(1, 0, 0), srid=settings.SRID))
        topo_point = TopologyMixin._topologypoint(lng, lat, None).reload()

        self.assertEquals(topo_point.paths.get(), closest_path)

        # Create one intervention by geometry (point/linestring)
        it_point = InterventionFactory.create(topology=topo_point)
        it_line = InterventionFactory.create(topology=topo_line)
        # reload
        it_point = type(it_point).objects.get(pk=it_point.pk)
        it_line = type(it_line).objects.get(pk=it_line.pk)

        proj = ProjectFactory.create()
        proj.interventions.add(it_point)
        proj.interventions.add(it_line)

        shp_creator = shape_exporter.ShapeCreator()

        # instanciate the class based view 'abnormally' to use create_shape directly
        # to avoid making http request, authent and reading from a zip
        pfl = ProjectFormatList()
        pfl.create_shape(shp_creator, Project.objects.all())

        self.assertEquals(len(shp_creator.shapes), 2)

        ds_point = gdal.DataSource(shp_creator.shapes[0][1])
        layer_point = ds_point[0]
        ds_line = gdal.DataSource(shp_creator.shapes[1][1])
        layer_line = ds_line[0]

        self.assertEquals(layer_point.geom_type.name, 'Point')
        self.assertEquals(layer_line.geom_type.name, 'LineString')

        for layer in [layer_point, layer_line]:
            self.assertEquals(layer.srs.name, 'RGF93_Lambert_93')
            self.assertItemsEqual(layer.fields,
                ['it_name', 'name', 'end_year', 'begin_year', 'cost', 'it_pk', 'id'])

        self.assertEquals(len(layer_point), 1)
        self.assertEquals(len(layer_line), 1)

        for feature in layer_point:
            self.assertEquals(str(feature['id']), str(proj.pk))
            self.assertEquals(str(feature['it_pk']), str(it_point.pk))
            self.assertTrue(feature.geom.geos.equals(it_point.geom))

        for feature in layer_line:
            self.assertEquals(str(feature['id']), str(proj.pk))
            self.assertEquals(str(feature['it_pk']), str(it_line.pk))
            self.assertTrue(feature.geom.geos.equals(it_line.geom))
