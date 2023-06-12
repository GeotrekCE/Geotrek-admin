import csv
from decimal import Decimal
from io import BytesIO, StringIO
import os
from collections import OrderedDict
from tempfile import TemporaryDirectory
from unittest import skipIf
from zipfile import ZipFile

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point, LineString, GeometryCollection
from django.contrib.gis import gdal
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate, deactivate_all

from geotrek.common.tests import CommonTest
from mapentity.tests.factories import SuperUserFactory
from mapentity.serializers.shapefile import ZipShapeSerializer

from geotrek.authent.tests.factories import PathManagerFactory, StructureFactory
from geotrek.core.tests.factories import StakeFactory
from geotrek.core.models import PathAggregation
from geotrek.common.tests.factories import OrganismFactory
from geotrek.common.tests import TranslationResetMixin
from geotrek.maintenance.models import Funding, Intervention, InterventionStatus, ManDay, Project
from geotrek.maintenance.views import InterventionFormatList, ProjectFormatList
from geotrek.core.tests.factories import PathFactory, TopologyFactory
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.land.tests.factories import (PhysicalEdgeFactory, LandEdgeFactory,
                                          CompetenceEdgeFactory, WorkManagementEdgeFactory,
                                          SignageManagementEdgeFactory)
from geotrek.outdoor.tests.factories import CourseFactory
from geotrek.signage.tests.factories import BladeFactory, SignageFactory
from geotrek.signage.models import Signage
from geotrek.maintenance.tests.factories import (InterventionFactory, InfrastructureInterventionFactory,
                                                 InterventionDisorderFactory, InterventionStatusFactory, ManDayFactory,
                                                 ProjectFactory, ContractorFactory, InterventionJobFactory,
                                                 SignageInterventionFactory, ProjectWithInterventionFactory)
from geotrek.trekking.tests.factories import POIFactory, TrekFactory, ServiceFactory


class InterventionViewsTest(CommonTest):
    model = Intervention
    modelfactory = InterventionFactory
    userfactory = PathManagerFactory
    extra_column_list = ['heliport_cost', 'subcontract_cost', 'disorders', 'jobs']
    expected_column_list_extra = ['id', 'name', 'heliport_cost', 'subcontract_cost', 'disorders', 'jobs']
    expected_column_formatlist_extra = ['id', 'heliport_cost', 'subcontract_cost', 'disorders', 'jobs']
    expected_json_geom = {'coordinates': [[3.0, 46.5],
                                          [3.001304, 46.5009004]],
                          'type': 'LineString'}

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

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

    def get_expected_datatables_attrs(self):
        return {
            'date': '30/03/2022',
            'id': self.obj.pk,
            'name': self.obj.name_display,
            'stake': self.obj.stake.stake,
            'status': self.obj.status.status,
            'type': self.obj.type.type,
            'target': self.obj.target_display
        }

    def test_creation_form_on_signage(self):
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
            land = LandEdgeFactory.create(paths=[(path, 0, .5)])
            physical = PhysicalEdgeFactory.create(paths=[(path, 0, .5)])
            competence = CompetenceEdgeFactory.create(paths=[(path, 0, .5)])
            workmanagement = WorkManagementEdgeFactory.create(paths=[(path, 0, .5)])
            signagemanagement = SignageManagementEdgeFactory.create(paths=[(path, 0, .5)])
            intervention_land = InterventionFactory.create(target=land)
            intervention_physical = InterventionFactory.create(target=physical)
            intervention_competence = InterventionFactory.create(target=competence)
            intervention_workmanagement = InterventionFactory.create(target=workmanagement)
            intervention_signagemanagement = InterventionFactory.create(target=signagemanagement)
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
        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertContains(response, intervention_land.target_display)
            self.assertContains(response, intervention_physical.target_display)
            self.assertContains(response, intervention_competence.target_display)
            self.assertContains(response, intervention_workmanagement.target_display)
            self.assertContains(response, intervention_signagemanagement.target_display)
        self.assertNotContains(response, intervention_other.target_display)

    def test_creation_form_on_signage_with_errors(self):
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
        data['name_en'] = 'modified'
        data['implantation_year'] = target_year
        data['access'] = ''
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
        data = self.get_good_data()
        data.pop('disorders')
        response = self.client.post(Intervention.get_add_url(), data)
        self.assertEqual(response.status_code, 302)

    def test_update_infrastructure(self):
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
        data['name_en'] = 'modified'
        data['implantation_year'] = target_year
        data['accessibility'] = ''
        data['access'] = ''
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
        good_data = self.get_good_data()
        good_data['stake'] = ''
        good_data['topology'] = """
        {"offset":0,"positions":{"0":[0.8298653170816073,1],"2":[0,0.04593024777973237]},"paths":[%s,%s,%s]}
        """ % (PathFactory.create().pk, PathFactory.create().pk, PathFactory.create().pk)
        response = self.client.post(Intervention.get_add_url(), good_data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.headers['location'])
        self.assertTrue('object' in response.context)
        intervention = response.context['object']
        self.assertFalse(intervention.stake is None)

    def test_form_deleted_projects(self):
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

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_csv_on_topology_multiple_paths(self):
        # We create an intervention on multiple paths and we check in csv target's field we have all the paths
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((4, 0), (8, 0)))
        InterventionFactory.create(target=TopologyFactory.create(paths=[(path_AB, 0.2, 1),
                                                                        (path_CD, 0, 1)]))
        response = self.client.get(self.model.get_format_list_url() + '?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')

        # Read the csv
        lines = list(csv.reader(StringIO(response.content.decode("utf-8")), delimiter=','))
        index_line = lines[0].index('On')
        self.assertEqual(lines[1][index_line],
                         f'Path: {path_AB.name} ({path_AB.pk}), Path: {path_CD.name} ({path_CD.pk})')

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

    def test_duplicate(self):
        super().test_duplicate()
        self.assertEqual(ManDay.objects.count(), 2)


class ProjectViewsTest(CommonTest):
    model = Project
    modelfactory = ProjectWithInterventionFactory
    userfactory = PathManagerFactory
    extra_column_list = ['domain', 'contractors']
    expected_column_list_extra = ['id', 'name', 'domain', 'contractors']
    expected_column_formatlist_extra = ['id', 'domain', 'contractors']
    expected_json_geom = {'type': 'GeometryCollection',
                          'geometries': [{'type': 'LineString', 'coordinates': [[3.0, 46.5], [3.001304, 46.5009004]]}]}

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

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

    def get_expected_datatables_attrs(self):
        return {
            'domain': None,
            'id': self.obj.pk,
            'name': self.obj.name_display,
            'period': self.obj.period_display,
            'type': None
        }

    def _check_update_geom_permission(self, response):
        pass

    def test_project_layer(self):
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
        self.assertEqual(features[0]['properties']['id'], p1.pk)

    def test_project_bbox_filter(self):
        p1 = ProjectFactory.create()
        ProjectFactory.create()
        ProjectFactory.create()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            t = TopologyFactory.create()
        else:
            t = TopologyFactory.create(geom='SRID=2154;POINT (700000 6600000)')
        InterventionFactory.create(project=p1, target=t)

        def jsonlist(bbox):
            url = self.model.get_datatablelist_url() + bbox
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            jsondict = response.json()
            return jsondict['data']

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
        response = self.client.get(project.get_detail_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, intervention.name)

        intervention.delete()

        response = self.client.get(project.get_detail_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, intervention.name)

    def test_duplicate(self):
        super().test_duplicate()
        self.assertEqual(Funding.objects.count(), 2)


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

        closest_path = PathFactory(geom=LineString(Point(0, 0), Point(1, 1), srid=settings.SRID))
        topo_point = TopologyFactory.create(paths=[(closest_path, 0.5, 0.5)])

        self.assertEqual(topo_point.paths.get(), closest_path)

        # Create one intervention by geometry (point/linestring/geometrycollection)
        it_point = InterventionFactory.create(target=topo_point)
        it_line = InterventionFactory.create(target=topo_line)
        course_point_a = Point(0, 0, srid=2154)
        course_point_b = Point(5, 5, srid=2154)
        course_line = LineString((0, 0), (1, 1), srid=2154)
        course_geometry_collection = GeometryCollection(course_point_a, course_point_b, course_line, srid=2154)

        course = CourseFactory.create(geom=course_geometry_collection)
        it_geometrycollection = InterventionFactory.create(target=course)
        # reload
        it_point = type(it_point).objects.get(pk=it_point.pk)
        it_line = type(it_line).objects.get(pk=it_line.pk)

        proj = ProjectFactory.create()
        proj.interventions.add(it_point)
        proj.interventions.add(it_line)
        proj.interventions.add(it_geometrycollection)

        # instanciate the class based view 'abnormally' to use create_shape directly
        # to avoid making http request, authent and reading from a zip
        pfl = ZipShapeSerializer()
        devnull = open(os.devnull, "wb")
        pfl.serialize(Project.objects.all(), stream=devnull, delete=False,
                      fields=ProjectFormatList().columns)
        shapefiles = pfl.path_directory
        shapefiles = [shapefile for shapefile in os.listdir(shapefiles) if shapefile[-3:] == "shp"]
        layers = {
            s: gdal.DataSource(os.path.join(pfl.path_directory, s))[0] for s in shapefiles
        }

        self.assertEqual(len(layers), 2)
        geom_type_layer = {layer.name: layer for layer in layers.values()}
        geom_types = geom_type_layer.keys()
        self.assertIn('MultiPoint', geom_types)
        self.assertIn('MultiLineString', geom_types)

        for layer in layers.values():
            self.assertRegex(layer.srs.name, "RGF.*93")
            self.assertCountEqual(layer.fields, [
                'id', 'name', 'period', 'type', 'domain', 'constraint',
                'global_cos', 'interventi', 'comments',
                'contractor', 'project_ow', 'project_ma', 'founders',
                'related_st', 'insertion_', 'update_dat',
                'cities', 'districts', 'restricted'
            ])

            self.assertEqual(len(layer), 1)
            self.assertEqual(len(layer), 1)
        for feature in geom_type_layer['MultiPoint']:
            self.assertEqual(str(feature['id']), str(proj.pk))
            self.assertEqual(len(feature.geom.geos), 3)
            geoms = {geos.wkt for geos in feature.geom.geos}
            self.assertSetEqual(geoms, {it_point.geom.wkt, course_point_a.wkt, course_point_b.wkt})

        for feature in geom_type_layer['MultiLineString']:
            self.assertEqual(str(feature['id']), str(proj.pk))
            self.assertEqual(len(feature.geom.geos), 2)
            geoms = {geos.wkt for geos in feature.geom.geos}
            self.assertSetEqual(geoms, {it_line.geom.wkt, course_line.wkt})


@override_settings(ENABLE_JOBS_COSTS_DETAILED_EXPORT=True)
class TestDetailedJobCostsExports(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

        cls.job1 = InterventionJobFactory(job="Worker", cost=12)
        cls.job2 = InterventionJobFactory(job="Streamer", cost=60)
        cls.job1_column_name = "Cost_Worker"
        cls.job2_column_name = "Cost_Streamer"
        cls.interv = InterventionFactory()
        cls.manday1 = ManDayFactory(nb_days=3, job=cls.job1, intervention=cls.interv)
        cls.manday2 = ManDayFactory(nb_days=2, job=cls.job2, intervention=cls.interv)

        cls.job3 = InterventionJobFactory(job="Banker", cost=5000)
        cls.job3_column_name = "Cost_Banker"

    def setUp(self):
        self.client.force_login(self.user)

    def test_detailed_mandays_export(self):
        '''Test detailed intervention job costs are exported properly, and follow data changes'''

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
        self.assertIn(f"Coût_{self.job2}", columns)
        qs = InterventionFormatList().get_queryset()
        interv_in_query_set = qs.get(id=self.interv.id)
        cost2_in_query_set = getattr(interv_in_query_set, f"Coût_{self.job2}")
        self.assertEqual(cost2_in_query_set, self.job2.cost * self.manday2.nb_days)
        deactivate_all()

    def test_csv_detailed_cost_content(self):
        '''Test CSV job costs exports contain accurate total price'''

        response = self.client.get('/intervention/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')

        # Assert right costs in CSV
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        for row in reader:
            self.assertEqual(Decimal(row[self.job1_column_name]), self.job1.cost * self.manday1.nb_days)
            self.assertEqual(Decimal(row[self.job2_column_name]), self.job2.cost * self.manday2.nb_days)

    def test_shp_detailed_cost_content(self):
        '''Test SHP job costs exports contain accurate total price'''
        signage = SignageFactory.create()
        InterventionFactory.create(target=signage)
        i_course = InterventionFactory.create(target=CourseFactory.create())
        ManDayFactory.create(intervention=i_course, nb_days=2)
        response = self.client.get('/intervention/list/export/?format=shp')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/zip')

        # Assert right costs in CSV
        with ZipFile(BytesIO(response.content)) as mzip:
            temp_directory = TemporaryDirectory()
            mzip.extractall(path=temp_directory.name)
            shapefiles = [shapefile for shapefile in os.listdir(temp_directory.name) if shapefile[-3:] == "shp"]
            layers = {
                s: gdal.DataSource(os.path.join(temp_directory.name, s))[0] for s in shapefiles
            }
            l_linestring = layers['LineString.shp']
            l_point = layers['Point.shp']
        feature_linestring = l_linestring[0]
        feature_point = l_point[0]
        self.assertEqual(Decimal(str(feature_linestring['cost_worke'])), self.job1.cost * self.manday1.nb_days)
        self.assertEqual(Decimal(str(feature_linestring['cost_strea'])), self.job2.cost * self.manday2.nb_days)
        self.assertIsNone(feature_point.get('cost_worke'))
        self.assertIsNone(feature_point.get('cost_strea'))


@override_settings(ENABLE_JOBS_COSTS_DETAILED_EXPORT=True)
class TestInterventionTargetExports(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.path = PathFactory(name="mypath")
        cls.interv = InterventionFactory(target=cls.path)

    def setUp(self):
        self.client.force_login(self.user)

    def test_csv_target_content(self):
        response = self.client.get('/intervention/list/export/', params={'format': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')

        # Assert right format in CSV
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        for row in reader:
            self.assertEqual(row["On"], f"Path: {self.path.name} ({self.path.pk})")
