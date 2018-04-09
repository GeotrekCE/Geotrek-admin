# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import Point, LineString
from django.contrib.gis import gdal
from django.test import TestCase
import json

from geotrek.common.tests import CommonTest
from mapentity.serializers.shapefile import ZipShapeSerializer, shapefile_files

from geotrek.authent.factories import PathManagerFactory
from geotrek.core.factories import StakeFactory
from geotrek.core.helpers import TopologyHelper
from geotrek.common.factories import OrganismFactory
from geotrek.common.tests import TranslationResetMixin
from geotrek.maintenance.models import Intervention, InterventionStatus, Project
from geotrek.maintenance.views import ProjectFormatList
from geotrek.core.factories import (PathFactory, PathAggregationFactory,
                                    TopologyFactory)
from geotrek.infrastructure.factories import InfrastructureFactory
from geotrek.signage.factories import SignageFactory
from geotrek.maintenance.factories import (InterventionFactory, InfrastructureInterventionFactory,
                                           InterventionDisorderFactory, InterventionStatusFactory,
                                           ProjectFactory, ContractorFactory, InterventionJobFactory,
                                           SignageInterventionFactory)


class InterventionViewsTest(CommonTest):
    model = Intervention
    modelfactory = InterventionFactory
    userfactory = PathManagerFactory

    def get_bad_data(self):
        return OrderedDict([
            ('name', ''),
            ('manday_set-TOTAL_FORMS', '0'),
            ('manday_set-INITIAL_FORMS', '1'),
            ('manday_set-MAX_NUM_FORMS', '0'),
        ]), 'This field is required.'

    def get_good_data(self):
        InterventionStatusFactory.create()
        good_data = {
            'name': 'test',
            'date': '2012-08-23',
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
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data['topology'] = '{"paths": [%s]}' % path.pk,
        else:
            good_data['topology'] = 'SRID=4326;POINT (5.1 6.6)'
        return good_data

    def test_creation_form_on_signage(self):
        self.login()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            signa = SignageFactory.create()
        else:
            signa = SignageFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        signage = u"%s" % signa

        response = self.client.get(Intervention.get_add_url() + '?signage=%s' % signa.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, signage)
        form = response.context['form']
        self.assertEqual(form.initial['signage'], signa)
        # Should be able to save form successfully
        data = self.get_good_data()
        data['signage'] = signa.pk
        response = self.client.post(Intervention.get_add_url() + '?signage=%s' % signa.pk, data)
        self.assertEqual(response.status_code, 302)

    def test_creation_form_on_signage_with_errors(self):
        self.login()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            signa = SignageFactory.create()
        else:
            signa = SignageFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        signage = u"%s" % signa

        response = self.client.get(Intervention.get_add_url() + '?signage=%s' % signa.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, signage)
        form = response.context['form']
        self.assertEqual(form.initial['signage'], signa)
        data = self.get_good_data()
        data['signage'] = signa.pk

        # If form invalid, it should not fail
        data.pop('status')
        response = self.client.post(Intervention.get_add_url() + '?signage=%s' % signa.pk, data)
        self.assertEqual(response.status_code, 200)

    def test_update_form_on_signage(self):
        self.login()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            signa = SignageFactory.create()
        else:
            signa = SignageFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        signage = u"%s" % signa

        intervention = InterventionFactory.create()
        self.assertIsNone(intervention.signage)
        intervention.set_topology(signa)
        intervention.save()
        self.assertIsNotNone(intervention.signage)
        response = self.client.get(intervention.get_update_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, signage)
        # Should be able to save form successfully
        form = response.context['form']
        data = form.initial
        data['disorders'] = data['disorders'][0].pk
        data['project'] = ''
        data['signage'] = form.fields['signage'].initial.pk  # because it is set after form init, not form.initial :(
        data.update(**{
            'manday_set-TOTAL_FORMS': '0',
            'manday_set-INITIAL_FORMS': '0',
            'manday_set-MAX_NUM_FORMS': '',
        })
        # Form URL is modified in form init
        formurl = intervention.get_update_url() + '?signage=%s' % signa.pk
        response = self.client.post(formurl, data)
        self.assertEqual(response.status_code, 302)

    def test_update_signage(self):
        self.login()
        target_year = 2017
        if settings.TREKKING_TOPOLOGY_ENABLED:
            intervention = SignageInterventionFactory.create()
        else:
            intervention = SignageInterventionFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        signa = intervention.signage
        # Save infrastructure form
        response = self.client.get(signa.get_update_url())
        form = response.context['form']
        data = form.initial
        data['name'] = 'modified'
        data['implantation_year'] = target_year
        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = '{"paths": [%s]}' % PathFactory.create().pk
        else:
            data['geom'] = 'SRID=4326;POINT (2.0 6.6)'
        data['manager'] = OrganismFactory.create().pk
        response = self.client.post(signa.get_update_url(), data)
        self.assertEqual(response.status_code, 302)
        # Check that intervention was not deleted (bug #783)
        intervention.reload()
        self.assertFalse(intervention.deleted)
        self.assertEqual(intervention.signage.name, 'modified')
        self.assertEqual(intervention.signage.implantation_year, target_year)

    def test_creation_form_on_infrastructure(self):
        self.login()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create()
        else:
            infra = InfrastructureFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        infrastr = "%s" % infra

        response = self.client.get(Intervention.get_add_url() + '?infrastructure=%s' % infra.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, infrastr)
        form = response.context['form']
        self.assertEqual(form.initial['infrastructure'], infra)
        # Should be able to save form successfully
        data = self.get_good_data()
        data['infrastructure'] = infra.pk
        response = self.client.post(Intervention.get_add_url() + '?infrastructure=%s' % infra.pk, data)
        self.assertEqual(response.status_code, 302)

    def test_creation_form_on_infrastructure_with_errors(self):
        self.login()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create()
        else:
            infra = InfrastructureFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        infrastr = "%s" % infra

        response = self.client.get(Intervention.get_add_url() + '?infrastructure=%s' % infra.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, infrastr)
        form = response.context['form']
        self.assertEqual(form.initial['infrastructure'], infra)
        data = self.get_good_data()
        data['infrastructure'] = infra.pk

        # If form invalid, it should not fail
        data.pop('status')
        response = self.client.post(Intervention.get_add_url() + '?infrastructure=%s' % infra.pk, data)
        self.assertEqual(response.status_code, 200)

    def test_update_form_on_infrastructure(self):
        self.login()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create()
        else:
            infra = InfrastructureFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        infrastr = "%s" % infra

        intervention = InterventionFactory.create()
        intervention.set_topology(infra)
        intervention.save()
        response = self.client.get(intervention.get_update_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, infrastr)
        # Should be able to save form successfully
        form = response.context['form']
        data = form.initial
        data['disorders'] = data['disorders'][0].pk
        data['project'] = ''
        data['infrastructure'] = form.fields['infrastructure'].initial.pk  # because it is set after form init, not form.initial :(
        data.update(**{
            'manday_set-TOTAL_FORMS': '0',
            'manday_set-INITIAL_FORMS': '0',
            'manday_set-MAX_NUM_FORMS': '',
        })
        # Form URL is modified in form init
        formurl = intervention.get_update_url() + '?infrastructure=%s' % infra.pk
        response = self.client.post(formurl, data)
        self.assertEqual(response.status_code, 302)

    def test_disorders_not_mandatory(self):
        self.login()
        data = self.get_good_data()
        data.pop('disorders')
        response = self.client.post(Intervention.get_add_url(), data)
        self.assertEqual(response.status_code, 302)

    def test_update_infrastructure(self):
        self.login()
        target_year = 2017
        if settings.TREKKING_TOPOLOGY_ENABLED:
            intervention = InfrastructureInterventionFactory.create()
        else:
            intervention = InfrastructureInterventionFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        infra = intervention.infrastructure
        # Save infrastructure form
        response = self.client.get(infra.get_update_url())
        form = response.context['form']
        data = form.initial
        data['name'] = 'modified'
        data['implantation_year'] = target_year
        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = '{"paths": [%s]}' % PathFactory.create().pk
        else:
            data['geom'] = 'SRID=4326;POINT (2.0 6.6)'
        response = self.client.post(infra.get_update_url(), data)
        self.assertEqual(response.status_code, 302)
        # Check that intervention was not deleted (bug #783)
        intervention.reload()
        self.assertFalse(intervention.deleted)
        self.assertEqual(intervention.infrastructure.name, 'modified')
        self.assertEqual(intervention.infrastructure.implantation_year, target_year)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_form_default_stake(self):
        """
        Without segmentation dynamic we do not have paths so we can't put any stake by default coming from paths
        """
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

    def test_form_deleted_projects(self):
        self.login()
        p1 = ProjectFactory.create()
        p2 = ProjectFactory.create()
        i = InterventionFactory.create(project=p1)
        response = self.client.get(i.get_update_url())
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        projects = form.fields['project'].queryset.all()
        self.assertItemsEqual(projects, [p1, p2])
        p2.delete()
        projects = form.fields['project'].queryset.all()
        self.assertItemsEqual(projects, [p1])

    def test_no_html_in_csv_infrastructure(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            InfrastructureInterventionFactory.create()
        else:
            InfrastructureInterventionFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        super(InterventionViewsTest, self).test_no_html_in_csv()

    def test_no_html_in_csv_signage(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            SignageInterventionFactory.create()
        else:
            SignageInterventionFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        super(InterventionViewsTest, self).test_no_html_in_csv()

    def test_structurerelated_not_loggedin(self):
        # Test that it does not fail on update if not logged in
        self.client.logout()
        response = self.client.get(Intervention.get_add_url())
        self.assertEqual(response.status_code, 302)

        i = InterventionFactory.create()
        response = self.client.get(i.get_update_url())
        self.assertEqual(response.status_code, 302)


class ProjectViewsTest(CommonTest):
    model = Project
    modelfactory = ProjectFactory
    userfactory = PathManagerFactory

    def get_bad_data(self):
        return OrderedDict([
            ('begin_year', ''),
            ('funding_set-TOTAL_FORMS', '0'),
            ('funding_set-INITIAL_FORMS', '1'),
            ('funding_set-MAX_NUM_FORMS', '0'),
        ]), 'This field is required.'

    def get_good_data(self):
        return {
            'name': 'test',
            'stake': '',
            'type': '',
            'domain': '',
            'begin_year': '2010',
            'end_year': '2012',
            'constraints': '',
            'global_cost': '12',
            'comments': '',
            'contractors': ContractorFactory.create().pk,
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

    def _check_update_geom_permission(self, response):
        pass

    def test_project_layer(self):
        self.login()
        p1 = ProjectFactory.create()
        ProjectFactory.create()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            InterventionFactory.create(project=p1)
        else:
            InterventionFactory.create(project=p1, geom='SRID=2154;POINT (700000 6600000)')

        # Check that only p1 is in geojson
        response = self.client.get(self.model.get_layer_url())
        self.assertEqual(response.status_code, 200)
        geojson = json.loads(response.content)
        features = geojson['features']

        self.assertEqual(len(Project.objects.all()), 2)
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]['properties']['pk'], p1.pk)

    def test_project_bbox_filter(self):
        self.login()

        p1 = ProjectFactory.create()
        ProjectFactory.create()
        ProjectFactory.create()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            t = TopologyFactory.create()
        else:
            t = TopologyFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        InterventionFactory.create(project=p1, topology=t)

        def jsonlist(bbox):
            url = self.model.get_jsonlist_url() + bbox
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            jsondict = json.loads(response.content)
            return jsondict['aaData']

        # Check that projects without interventions are always present
        self.assertEqual(len(Project.objects.all()), 3)
        self.assertEqual(len(jsonlist('')), 3)
        self.assertEqual(len(jsonlist('?bbox=POLYGON((1%202%200%2C1%202%200%2C1%202%200%2C1%202%200%2C1%202%200))')), 2)

        # Give a bbox that match intervention, and check that all 3 projects are back
        bbox = '?bbox=POLYGON((2.9%2046.4%2C%203.1%2046.4%2C%203.1%2046.6%2C%202.9%2046.6%2C%202.9%2046.4))'
        self.assertEqual(len(jsonlist(bbox)), 3)

    def test_deleted_interventions(self):
        project = ProjectFactory.create()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            intervention = InterventionFactory.create()
        else:
            intervention = InterventionFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        project.interventions.add(intervention)

        self.login()
        response = self.client.get(project.get_detail_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, intervention.name)

        intervention.delete()

        response = self.client.get(project.get_detail_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, intervention.name)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class ExportTest(TranslationResetMixin, TestCase):

    def test_shape_mixed(self):
        """
        Test that a project made of intervention of different geom create multiple files.
        Check that those files are each of a different type (Point/LineString) and that
        the project and the intervention are correctly referenced in it.
        """

        # Create topology line
        topo_line = TopologyFactory.create(no_path=True)
        line = PathFactory.create(geom=LineString(Point(10, 10), Point(11, 10)))
        PathAggregationFactory.create(topo_object=topo_line, path=line)

        # Create a topology point
        lng, lat = tuple(Point(1, 1, srid=settings.SRID).transform(settings.API_SRID, clone=True))

        closest_path = PathFactory(geom=LineString(Point(0, 0), Point(1, 0), srid=settings.SRID))
        topo_point = TopologyHelper._topologypoint(lng, lat, None).reload()

        self.assertEquals(topo_point.paths.get(), closest_path)

        # Create one intervention by geometry (point/linestring)
        it_point = InterventionFactory.create(topology=topo_point)
        it_line = InterventionFactory.create(topology=topo_line)
        # reload
        it_point = type(it_point).objects.get(pk=it_point.pk)
        it_line = type(it_line).objects.get(pk=it_line.pk)

        proj = ProjectFactory.create()
        proj.interventions.add(it_point)
        proj.interventions.add(it_line)

        # instanciate the class based view 'abnormally' to use create_shape directly
        # to avoid making http request, authent and reading from a zip
        pfl = ZipShapeSerializer()
        devnull = open(os.devnull, "wb")
        pfl.serialize(Project.objects.all(), stream=devnull, delete=False,
                      fields=ProjectFormatList.columns)
        self.assertEquals(len(pfl.layers), 2)

        ds_point = gdal.DataSource(pfl.layers.values()[0])
        layer_point = ds_point[0]
        ds_line = gdal.DataSource(pfl.layers.values()[1])
        layer_line = ds_line[0]

        self.assertEquals(layer_point.geom_type.name, 'MultiPoint')
        self.assertEquals(layer_line.geom_type.name, 'LineString')

        for layer in [layer_point, layer_line]:
            self.assertEquals(layer.srs.name, 'RGF93_Lambert_93')
            self.assertItemsEqual(layer.fields, [
                'id', 'name', 'period', 'type', 'domain', 'constraint',
                'global_cos', 'interventi', 'interven_1', 'comments',
                'contractor', 'project_ow', 'project_ma', 'founders',
                'related_st', 'insertion_', 'update_dat',
                'cities', 'districts', 'restricted'
            ])

        self.assertEquals(len(layer_point), 1)
        self.assertEquals(len(layer_line), 1)

        for feature in layer_point:
            self.assertEquals(str(feature['id']), str(proj.pk))
            self.assertEquals(len(feature.geom.geos), 1)
            self.assertAlmostEqual(feature.geom.geos[0].x, it_point.geom.x)
            self.assertAlmostEqual(feature.geom.geos[0].y, it_point.geom.y)

        for feature in layer_line:
            self.assertEquals(str(feature['id']), str(proj.pk))
            self.assertTrue(feature.geom.geos.equals(it_line.geom))

        # Clean-up temporary shapefiles
        for layer_file in pfl.layers.values():
            for subfile in shapefile_files(layer_file):
                os.remove(subfile)
