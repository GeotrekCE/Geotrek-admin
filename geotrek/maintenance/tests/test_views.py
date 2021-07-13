import csv
from decimal import Decimal
from io import StringIO
import os
from collections import OrderedDict
from unittest import skipIf

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point, LineString
from django.contrib.gis import gdal
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate

from geotrek.common.tests import CommonTest
from mapentity.factories import SuperUserFactory
from mapentity.serializers.shapefile import ZipShapeSerializer

from geotrek.authent.factories import PathManagerFactory, StructureFactory
from geotrek.core.factories import StakeFactory
from geotrek.core.models import PathAggregation
from geotrek.common.factories import OrganismFactory
from geotrek.common.tests import TranslationResetMixin
from geotrek.maintenance.models import Intervention, InterventionStatus, Project
from geotrek.maintenance.views import InterventionFormatList, ProjectFormatList
from geotrek.core.factories import PathFactory, TopologyFactory
from geotrek.core.models import Topology
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.factories import InfrastructureFactory
from geotrek.signage.factories import BladeFactory, SignageFactory
from geotrek.signage.models import Signage
from geotrek.maintenance.factories import (InterventionFactory, InfrastructureInterventionFactory,
                                           InterventionDisorderFactory, InterventionStatusFactory, ManDayFactory,
                                           ProjectFactory, ContractorFactory, InterventionJobFactory,
                                           SignageInterventionFactory, ProjectWithInterventionFactory)
from geotrek.trekking.factories import POIFactory, TrekFactory, ServiceFactory


class InterventionViewsTest(CommonTest):
    model = Intervention
    modelfactory = InterventionFactory
    userfactory = PathManagerFactory
    get_expected_json_attrs = None  # Disable API tests

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
        signage = "%s" % signa

        response = self.client.get('%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                                       signa.pk,
                                                                       ContentType.objects.get_for_model(Signage).pk
                                                                       ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, signage)
        # Should be able to save form successfully
        data = self.get_good_data()
        response = self.client.post('%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                                        signa.pk,
                                                                        ContentType.objects.get_for_model(Signage).pk
                                                                        ),
                                    data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(signa, Intervention.objects.get().target)

    def test_detail_target_objects(self):
        self.login()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create(geom=LineString((200, 200), (300, 300)))
            signa = SignageFactory.create(paths=[(path, .5, .5)])
            signa.save()
            infrastructure = InfrastructureFactory.create(paths=[(path, .5, .5)])
            infrastructure.save()
            poi = POIFactory.create(paths=[(path, .5, .5)])
            trek = TrekFactory.create(paths=[(path, .5, .5)])
            service = ServiceFactory.create(paths=[(path, .5, .5)])
            topo = TopologyFactory.create(paths=[(path, .5, .5)])
            topo.save()

            path_other = PathFactory.create(geom=LineString((10000, 0), (10010, 0)))
            signa_other = SignageFactory.create(paths=[(path_other, .5, .5)])
            signa_other.save()
        else:
            signa = SignageFactory.create(geom='SRID=2154;POINT (250 250)')
            infrastructure = InfrastructureFactory.create(geom='SRID=2154;POINT (250 250)')
            poi = POIFactory.create(geom='SRID=2154;POINT (250 250)')
            trek = TrekFactory.create(geom='SRID=2154;POINT (250 250)')
            service = ServiceFactory.create(geom='SRID=2154;POINT (250 250)')
            topo = TopologyFactory.create(geom='SRID=2154;POINT (250 250)')

            signa_other = SignageFactory.create(geom='SRID=2154;POINT (10005 0)')

        intervention_signa = InterventionFactory.create(target=signa)
        intervention_infra = InterventionFactory.create(target=infrastructure)
        intervention_poi = InterventionFactory.create(target=poi)
        intervention_trek = InterventionFactory.create(target=trek)
        intervention_service = InterventionFactory.create(target=service)
        intervention_topo = InterventionFactory.create(target=topo)
        blade = BladeFactory(signage=signa, number="1")
        intervention_blade = InterventionFactory.create(target=blade)

        intervention_other = InterventionFactory.create(target=signa_other)

        response = self.client.get(signa.get_detail_url())
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, intervention_signa.target_display)
        self.assertContains(response, intervention_infra.target_display)
        self.assertContains(response, intervention_poi.target_display)
        self.assertContains(response, intervention_trek.target_display)
        self.assertContains(response, intervention_service.target_display)
        self.assertContains(response, intervention_blade.target_display)
        self.assertContains(response, intervention_topo.target_display)

        self.assertNotContains(response, intervention_other.target_display)

    def test_creation_form_on_signage_with_errors(self):
        self.login()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            signa = SignageFactory.create()
        else:
            signa = SignageFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        signage = "%s" % signa

        response = self.client.get('%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                                       signa.pk,
                                                                       ContentType.objects.get_for_model(Signage).pk
                                                                       ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, signage)
        data = self.get_good_data()

        # If form invalid, it should not fail
        data.pop('status')
        response = self.client.post('%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                                        signa.pk,
                                                                        ContentType.objects.get_for_model(Signage).pk
                                                                        ),
                                    data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Intervention.objects.exists())

    def test_update_form_on_signage(self):
        self.login()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            signa = SignageFactory.create()
        else:
            signa = SignageFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        signage = "%s" % signa

        intervention = InterventionFactory.create(target=signa)
        response = self.client.get(intervention.get_update_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, signage)
        # Should be able to save form successfully
        form = response.context['form']
        data = form.initial
        data['disorders'] = data['disorders'][0].pk
        data['project'] = ''
        data.update(**{
            'manday_set-TOTAL_FORMS': '0',
            'manday_set-INITIAL_FORMS': '0',
            'manday_set-MAX_NUM_FORMS': '',
        })
        # Form URL is modified in form init
        formurl = '%s?target_id=%s&target_type=%s' % (intervention.get_update_url(), signa.pk, ContentType.objects.get_for_model(Signage).pk)
        response = self.client.post(formurl, data)
        self.assertEqual(response.status_code, 302)

    def test_update_signage(self):
        self.login()
        target_year = 2017
        if settings.TREKKING_TOPOLOGY_ENABLED:
            intervention = SignageInterventionFactory.create()
        else:
            intervention = SignageInterventionFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        signa = intervention.target
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
        intervention = Intervention.objects.first()
        self.assertFalse(intervention.deleted)
        self.assertEqual(intervention.target.name, 'modified')
        self.assertEqual(intervention.target.implantation_year, target_year)

    def test_creation_form_on_infrastructure(self):
        self.login()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create()
        else:
            infra = InfrastructureFactory.create(geom='SRID=2154;POINT (700000 6600000)')

        response = self.client.get('%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                                       infra.pk,
                                                                       ContentType.objects.get_for_model(Infrastructure).pk))
        self.assertEqual(response.status_code, 200)
        # Should be able to save form successfully
        data = self.get_good_data()
        response = self.client.post('%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                                        infra.pk,
                                                                        ContentType.objects.get_for_model(Infrastructure).pk),
                                    data)
        self.assertEqual(response.status_code, 302)

    def test_creation_form_on_infrastructure_with_errors(self):
        self.login()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create()
        else:
            infra = InfrastructureFactory.create(geom='SRID=2154;POINT (700000 6600000)')

        response = self.client.get('%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                                       infra.pk,
                                                                       ContentType.objects.get_for_model(Infrastructure).pk))
        self.assertEqual(response.status_code, 200)
        data = self.get_good_data()

        # If form invalid, it should not fail
        data.pop('status')
        response = self.client.post('%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                                        infra.pk,
                                                                        ContentType.objects.get_for_model(Infrastructure).pk), data)
        self.assertEqual(response.status_code, 200)

    def test_update_form_on_infrastructure(self):
        self.login()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create()
        else:
            infra = InfrastructureFactory.create(geom='SRID=2154;POINT (700000 6600000)')

        intervention = InterventionFactory.create(target=infra)
        response = self.client.get(intervention.get_update_url())
        self.assertEqual(response.status_code, 200)
        # Should be able to save form successfully
        form = response.context['form']
        data = form.initial
        data['disorders'] = data['disorders'][0].pk
        data['project'] = ''
        data.update(**{
            'manday_set-TOTAL_FORMS': '0',
            'manday_set-INITIAL_FORMS': '0',
            'manday_set-MAX_NUM_FORMS': '',
        })
        # Form URL is modified in form init
        formurl = '%s?target_id=%s&target_type=%s' % (Intervention.get_add_url(),
                                                      infra.pk,
                                                      ContentType.objects.get_for_model(Infrastructure).pk)
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
        infra = intervention.target
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
        intervention = Intervention.objects.first()
        self.assertFalse(intervention.deleted)
        self.assertEqual(intervention.target.name, 'modified')
        self.assertEqual(intervention.target.implantation_year, target_year)

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
        self.assertCountEqual(projects, [p1, p2])
        p2.delete()
        projects = form.fields['project'].queryset.all()
        self.assertCountEqual(projects, [p1])

    def test_no_html_in_csv_infrastructure(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            InfrastructureInterventionFactory.create()
        else:
            InfrastructureInterventionFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        super().test_no_html_in_csv()

    def test_no_html_in_csv_signage(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            SignageInterventionFactory.create()
        else:
            SignageInterventionFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        super().test_no_html_in_csv()

    def test_structurerelated_not_loggedin(self):
        # Test that it does not fail on update if not logged in
        self.client.logout()
        response = self.client.get(Intervention.get_add_url())
        self.assertEqual(response.status_code, 302)

        i = InterventionFactory.create()
        response = self.client.get(i.get_update_url())
        self.assertEqual(response.status_code, 302)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_creation_form_line(self):
        path = PathFactory.create(geom=LineString(Point(700000, 6600000), Point(700300, 6600300), srid=settings.SRID))
        self.super_user = SuperUserFactory.create(username='admin', password='super')
        self.client.login(username='admin', password='super')
        data = self.get_good_data()
        data['structure'] = StructureFactory.create().pk
        data['topology'] = '{"paths": [%s], "positions":{"0":[0,1]}}' % path.pk,
        response = self.client.post('%s' % (Intervention.get_add_url()),
                                    data)
        self.assertEqual(PathAggregation.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Intervention.objects.first().geom, path.geom)
        self.assertEqual(Intervention.objects.first().target.kind, 'INTERVENTION')


class ProjectViewsTest(CommonTest):
    model = Project
    modelfactory = ProjectWithInterventionFactory
    userfactory = PathManagerFactory
    get_expected_json_attrs = None  # Disable API tests

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
        geojson = response.json()
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
        InterventionFactory.create(project=p1, target=t)

        def jsonlist(bbox):
            url = self.model.get_jsonlist_url() + bbox
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            jsondict = response.json()
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

        line = PathFactory.create(geom=LineString(Point(10, 10), Point(11, 10)))
        topo_line = TopologyFactory.create(paths=[line])

        # Create a topology point
        lng, lat = tuple(Point(1, 1, srid=settings.SRID).transform(settings.API_SRID, clone=True))

        closest_path = PathFactory(geom=LineString(Point(0, 0), Point(1, 0), srid=settings.SRID))
        topo_point = Topology._topologypoint(lng, lat, None)
        topo_point.save()

        self.assertEqual(topo_point.paths.get(), closest_path)

        # Create one intervention by geometry (point/linestring)
        it_point = InterventionFactory.create(target=topo_point)
        it_line = InterventionFactory.create(target=topo_line)
        # reload
        it_point = type(it_point).objects.get(pk=it_point.pk)
        it_line = type(it_line).objects.get(pk=it_line.pk)

        proj = ProjectFactory.create()
        proj.interventions.add(it_point)
        proj.interventions.add(it_line)

        # instanciate the class based view 'abnormally' to use create_shape directly
        # to avoid making http request, authent and reading from a zip
        pfl = ZipShapeSerializer()
        shapefiles = pfl.path_directory
        devnull = open(os.devnull, "wb")
        pfl.serialize(Project.objects.all(), stream=devnull, delete=False,
                      fields=ProjectFormatList.columns)
        shapefiles = [shapefile for shapefile in os.listdir(shapefiles) if shapefile[-3:] == "shp"]
        datasources = [gdal.DataSource(os.path.join(pfl.path_directory, s)) for s in shapefiles]
        layers = [ds[0] for ds in datasources]

        self.assertEqual(len(datasources), 2)
        geom_type_layer = {layer.name: layer for layer in layers}
        geom_types = geom_type_layer.keys()
        self.assertIn('MultiPoint', geom_types)
        self.assertIn('MultiLineString', geom_types)

        for layer in layers:
            self.assertEqual(layer.srs.name, 'RGF93_Lambert_93')
            self.assertCountEqual(layer.fields, [
                'id', 'name', 'period', 'type', 'domain', 'constraint',
                'global_cos', 'interventi', 'comments',
                'contractor', 'project_ow', 'project_ma', 'founders',
                'related_st', 'insertion_', 'update_dat',
                'cities', 'districts', 'restricted'
            ])

        self.assertEqual(len(layers[0]), 1)
        self.assertEqual(len(layers[1]), 1)

        for feature in geom_type_layer['MultiPoint']:
            self.assertEqual(str(feature['id']), str(proj.pk))
            self.assertEqual(len(feature.geom.geos), 1)
            self.assertAlmostEqual(feature.geom.geos[0].x, it_point.geom.x)
            self.assertAlmostEqual(feature.geom.geos[0].y, it_point.geom.y)

        for feature in geom_type_layer['MultiLineString']:
            self.assertEqual(str(feature['id']), str(proj.pk))
            self.assertTrue(feature.geom.geos.equals(it_line.geom))


@override_settings(ENABLE_JOBS_COSTS_DETAILED_EXPORT=True)
class TestDetailedJobCostsExports(TestCase):

    def setUp(self):
        self.user = SuperUserFactory.create()
        self.client.force_login(self.user)

        self.job1 = InterventionJobFactory(job="Worker", cost=12)
        self.job2 = InterventionJobFactory(job="Streamer", cost=60)
        self.job1_column_name = "Cost Worker"
        self.job2_column_name = "Cost Streamer"
        self.interv = InterventionFactory()
        self.manday1 = ManDayFactory(nb_days=3, job=self.job1, intervention=self.interv)
        self.manday2 = ManDayFactory(nb_days=2, job=self.job2, intervention=self.interv)

        self.job3 = InterventionJobFactory(job="Banker", cost=5000)
        self.job3_column_name = "Cost Banker"

    def test_detailed_mandays_export(self):
        # Assert each job used in intervention has a column in export view
        columns = InterventionFormatList().columns
        self.assertIn(self.job1_column_name, columns)
        self.assertIn(self.job2_column_name, columns)

        # Assert no duplicate in column exports
        self.assertEqual(len(columns), len(set(columns)))

        # Assert job not used in intervention is not exported
        self.assertNotIn(self.job3_column_name, columns)

        # Assert queryset contains right amount for each cost
        qs = InterventionFormatList().get_queryset()
        interv_in_query_set = qs.get(id=self.interv.id)

        cost1_in_query_set = getattr(interv_in_query_set, self.job1_column_name)
        self.assertEqual(cost1_in_query_set, self.job1.cost * self.manday1.nb_days)

        cost2_in_query_set = getattr(interv_in_query_set, self.job2_column_name)
        self.assertEqual(cost2_in_query_set, self.job2.cost * self.manday2.nb_days)

        # Assert cost is calculated properly when we add and remove mandays on the same job
        # Add manday and refresh
        manday1bis = ManDayFactory(nb_days=1, job=self.job1, intervention=self.interv)
        qs = InterventionFormatList().get_queryset()
        interv_in_query_set = qs.get(id=self.interv.id)
        cost1_in_query_set = getattr(interv_in_query_set, self.job1_column_name)
        self.assertEqual(cost1_in_query_set, self.job1.cost * (self.manday1.nb_days + manday1bis.nb_days))
        # Remove manday and refresh
        manday1bis.delete()
        qs = InterventionFormatList().get_queryset()
        interv_in_query_set = qs.get(id=self.interv.id)
        cost1_in_query_set = getattr(interv_in_query_set, self.job1_column_name)
        self.assertEqual(cost1_in_query_set, self.job1.cost * self.manday1.nb_days)

        # Assert deleted manday does not create an entry
        self.manday1.delete()
        columns = InterventionFormatList().columns
        self.assertNotIn(self.job1_column_name, columns)

        # Test column translations don't mess it up
        activate('fr')
        columns = InterventionFormatList().columns
        self.assertIn(f"Coût {self.job2}", columns)
        qs = InterventionFormatList().get_queryset()
        interv_in_query_set = qs.get(id=self.interv.id)
        cost2_in_query_set = getattr(interv_in_query_set, f"Coût {self.job2}")
        self.assertEqual(cost2_in_query_set, self.job2.cost * self.manday2.nb_days)

    def test_csv_detailed_cost_content(self):
        response = self.client.get('/intervention/list/export/', params={'format': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')

        # Assert right costs in CSV
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        for row in reader:
            self.assertEqual(Decimal(row[self.job1_column_name]), self.job1.cost * self.manday1.nb_days)
            self.assertEqual(Decimal(row[self.job2_column_name]), self.job2.cost * self.manday2.nb_days)
