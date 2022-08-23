import datetime

from django.conf import settings
from django.test import TestCase

from geotrek.common.tests import CommonTest, GeotrekAPITestCase
from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import PathManagerFactory
from geotrek.maintenance.tests.factories import InterventionFactory
from geotrek.infrastructure.models import (Infrastructure, InfrastructureCondition, INFRASTRUCTURE_TYPES)
from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.tests.factories import (InfrastructureFactory, InfrastructureNoPictogramFactory,
                                                    InfrastructureTypeFactory, InfrastructureConditionFactory,
                                                    PointInfrastructureFactory)
from geotrek.infrastructure.filters import InfrastructureFilterSet


class InfrastructureTest(TestCase):
    def test_helpers(self):
        p = PathFactory.create()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create(paths=[p])
        else:
            infra = InfrastructureFactory.create(geom=p.geom)

        self.assertCountEqual(p.infrastructures, [infra])


class InfrastructureViewsTest(GeotrekAPITestCase, CommonTest):
    model = Infrastructure
    modelfactory = InfrastructureFactory
    userfactory = PathManagerFactory
    expected_json_geom = {'type': 'LineString', 'coordinates': [[3.0, 46.5], [3.001304, 46.5009004]]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'checkbox', 'name', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'type', 'eid']

    def get_expected_json_attrs(self):
        return {
            'accessibility': '',
            'name': self.obj.name,
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False}
            ],
            'structure': {
                'id': self.obj.structure.pk,
                'name': self.obj.structure.name,
            },
            'type': {
                'id': self.obj.type.pk,
                'label': self.obj.type.label,
                'pictogram': self.obj.type.pictogram.url if self.obj.type.pictogram else '/static/infrastructure/picto-infrastructure.png',
            },
        }

    def get_expected_datatables_attrs(self):
        return {
            'cities': '[]',
            'condition': self.obj.condition.label,
            'id': self.obj.pk,
            'checkbox': self.obj.checkbox_display,
            'name': self.obj.name_display,
            'type': self.obj.type.label,
        }

    def get_good_data(self):
        good_data = {
            'name_fr': 'test',
            'name_en': 'test_en',
            'description': 'oh',
            'type': InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING).pk,
            'condition': InfrastructureConditionFactory.create().pk,
            'accessibility': 'description accessibility'
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data['topology'] = '{"paths": [%s]}' % path.pk
        else:
            good_data['geom'] = 'LINESTRING (0.0 0.0, 1.0 1.0)'
        return good_data

    def test_description_in_detail_page(self):
        infra = InfrastructureFactory.create(description="<b>Beautiful !</b>")
        response = self.client.get(infra.get_detail_url())
        self.assertContains(response, "<b>Beautiful !</b>")

    def test_check_structure_or_none_related_are_visible(self):
        infratype = InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING, structure=None)
        response = self.client.get(self.model.get_add_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        form = response.context['form']
        type = form.fields['type']
        self.assertTrue((infratype.pk, str(infratype)) in type.choices)

    def test_no_pictogram(self):
        self.modelfactory = InfrastructureNoPictogramFactory
        super().test_api_detail_for_model()


class PointInfrastructureViewsTest(InfrastructureViewsTest):
    modelfactory = PointInfrastructureFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [3.0, 46.5]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'checkbox', 'name', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'type', 'eid']

    def get_good_data(self):
        good_data = {
            'accessibility': 'description accessibility',
            'name_fr': 'test',
            'name_en': 'test_en',
            'description': 'oh',
            'type': InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING).pk,
            'condition': InfrastructureConditionFactory.create().pk,
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data['topology'] = '{"paths": [%s]}' % path.pk
        else:
            good_data['geom'] = 'POINT(0.42 0.666)'
        return good_data


class InfrastructureConditionTest(TestCase):
    def test_manager(self):
        it1 = InfrastructureConditionFactory.create()
        it2 = InfrastructureConditionFactory.create()
        it3 = InfrastructureConditionFactory.create()

        self.assertCountEqual(InfrastructureCondition.objects.all(), [it1, it2, it3])


class InfraFilterTestMixin:
    factory = None
    filterset = None

    def login(self):
        user = PathManagerFactory(password='booh')
        self.client.force_login(user=user)

    def test_intervention_filter(self):
        self.login()

        model = self.factory._meta.model
        # We will filter by this year
        year = 2014
        good_date_year = datetime.datetime(year=year, month=2, day=2)
        bad_date_year = datetime.datetime(year=year + 2, month=2, day=2)

        # Bad topology/infrastructure: No intervention
        self.factory()

        # Bad signage: intervention with wrong year
        bad_topo = self.factory()
        InterventionFactory(target=bad_topo, date=bad_date_year)

        # Good signage: intervention with the good year
        good_topo = self.factory()
        InterventionFactory(target=good_topo, date=good_date_year)

        data = {
            'intervention_year': year
        }
        response = self.client.get(model.get_datatablelist_url(), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 1)

    def test_duplicate_implantation_year_filter(self):
        self.login()

        model = self.factory._meta.model
        # We will check if this
        year = 2014
        year_t = datetime.datetime(year=year, month=2, day=2)

        # Bad signage: intervention with wrong year
        topo_1 = self.factory()
        InterventionFactory(target=topo_1, date=year_t)

        # Good signage: intervention with the good year
        topo_2 = self.factory()
        InterventionFactory(target=topo_2, date=year_t)

        response = self.client.get(model.get_list_url())
        self.assertContains(response, '<option value="2014">2014</option>', count=1)


class InfrastructureFilterTest(InfraFilterTestMixin, AuthentFixturesTest):
    factory = InfrastructureFactory
    filterset = InfrastructureFilterSet

    def test_none_implantation_year_filter(self):
        self.login()
        model = self.factory._meta.model
        InfrastructureFactory.create()
        response = self.client.get(model.get_list_url())
        self.assertFalse('option value="" selected>None</option' in str(response))

    def test_implantation_year_filter(self):
        self.login()
        model = self.factory._meta.model
        i = InfrastructureFactory.create(implantation_year=2015)
        i2 = InfrastructureFactory.create(implantation_year=2016)
        response = self.client.get(model.get_list_url())

        self.assertContains(response, '<option value="2015">2015</option>')
        self.assertContains(response, '<option value="2016">2016</option>')

        filter = InfrastructureFilterSet(data={'implantation_year': [2015]})
        self.assertTrue(i in filter.qs)
        self.assertFalse(i2 in filter.qs)

    def test_implantation_year_filter_with_str(self):
        filter = InfrastructureFilterSet(data={'implantation_year': 'toto'})
        self.login()
        model = self.factory._meta.model
        i = InfrastructureFactory.create(implantation_year=2015)
        i2 = InfrastructureFactory.create(implantation_year=2016)
        response = self.client.get(model.get_list_url())

        self.assertContains(response, '<option value="2015">2015</option>')
        self.assertContains(response, '<option value="2016">2016</option>')

        self.assertIn(i, filter.qs)
        self.assertIn(i2, filter.qs)
