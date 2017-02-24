# -*- coding: utf-8 -*-
import datetime
import json

from django.test import TestCase

from geotrek.common.tests import CommonTest
from geotrek.authent.tests import AuthentFixturesTest
from geotrek.authent.models import default_structure
from geotrek.authent.factories import PathManagerFactory
from geotrek.maintenance.factories import InterventionFactory
from geotrek.infrastructure.models import (Infrastructure, InfrastructureType,
                                           InfrastructureCondition, Signage,
                                           INFRASTRUCTURE_TYPES)
from geotrek.core.factories import PathFactory, PathAggregationFactory
from geotrek.infrastructure.factories import (SignageFactory, InfrastructureFactory,
                                              InfrastructureTypeFactory, InfrastructureConditionFactory)
from geotrek.infrastructure.filters import SignageFilterSet, InfrastructureFilterSet


class InfrastructureTest(TestCase):
    def test_helpers(self):
        p = PathFactory.create()

        self.assertEquals(len(p.infrastructures), 0)
        sign = SignageFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=sign, path=p,
                                      start_position=0.5, end_position=0.5)

        self.assertItemsEqual(p.signages, [sign])

        infra = InfrastructureFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=infra, path=p)

        self.assertItemsEqual(p.infrastructures, [infra])


class InfrastructureViewsTest(CommonTest):
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
            'condition': InfrastructureConditionFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def test_description_in_detail_page(self):
        infra = InfrastructureFactory.create(description="<b>Beautiful !</b>")
        self.login()
        response = self.client.get(infra.get_detail_url())
        self.assertContains(response, "<b>Beautiful !</b>")


class PointInfrastructureViewsTest(InfrastructureViewsTest):
    def get_good_data(self):
        PathFactory.create()
        return {
            'name': 'test',
            'description': 'oh',
            'structure': default_structure().pk,
            'type': InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING).pk,
            'condition': InfrastructureConditionFactory.create().pk,
            'topology': '{"lat": 0.42, "lng": 0.666}'
        }


class SignageViewsTest(InfrastructureViewsTest):
    model = Signage
    modelfactory = SignageFactory

    def get_good_data(self):
        data = super(SignageViewsTest, self).get_good_data()
        data['type'] = InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.SIGNAGE).pk
        data['condition'] = InfrastructureConditionFactory.create().pk
        return data


class InfrastructureTypeTest(TestCase):
    def test_manager(self):
        it1 = InfrastructureTypeFactory.create()
        it2 = InfrastructureTypeFactory.create()
        it3 = InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.SIGNAGE)

        self.assertNotEqual(InfrastructureType.objects.for_signages(),
                            InfrastructureType.objects.for_infrastructures())
        self.assertItemsEqual(InfrastructureType.objects.for_signages(), [it3])
        self.assertItemsEqual(InfrastructureType.objects.for_infrastructures(),
                              [it1, it2])
        self.assertItemsEqual(InfrastructureType.objects.all(), [it1, it2, it3])


class InfrastructureConditionTest(TestCase):
    def test_manager(self):
        it1 = InfrastructureConditionFactory.create()
        it2 = InfrastructureConditionFactory.create()
        it3 = InfrastructureConditionFactory.create()

        self.assertItemsEqual(InfrastructureCondition.objects.all(), [it1, it2, it3])


class InfraFilterTestMixin():
    factory = None
    filterset = None

    def login(self):
        user = PathManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

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
        InterventionFactory(topology=bad_topo, date=bad_date_year)

        # Good signage: intervention with the good year
        good_topo = self.factory()
        InterventionFactory(topology=good_topo, date=good_date_year)

        data = {
            'intervention_year': year
        }
        response = self.client.get(model.get_jsonlist_url(), data)

        self.assertEqual(response.status_code, 200)
        topo_pk = json.loads(response.content)['map_obj_pk']

        self.assertItemsEqual(topo_pk, [good_topo.pk])

    def test_intervention_filter_has_correct_label(self):
        self.login()
        model = self.factory._meta.model
        response = self.client.get(model.get_list_url())
        self.assertContains(response, '<option value="-1">Intervention year</option>')


class SignageFilterTest(InfraFilterTestMixin, AuthentFixturesTest):
    factory = SignageFactory
    filterset = SignageFilterSet


class InfrastructureFilterTest(InfraFilterTestMixin, AuthentFixturesTest):
    factory = InfrastructureFactory
    filterset = InfrastructureFilterSet
