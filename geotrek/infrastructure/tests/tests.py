# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from django.utils import simplejson

from geotrek.mapentity.tests import MapEntityTest
from geotrek.authent.models import default_structure
from geotrek.authent.factories import PathManagerFactory
from geotrek.maintenance.factories import InterventionFactory

from geotrek.infrastructure.models import (Infrastructure, InfrastructureType,
    Signage, INFRASTRUCTURE_TYPES)
from geotrek.core.factories import PathFactory, PathAggregationFactory
from geotrek.infrastructure.factories import (SignageFactory,
    InfrastructureFactory, InfrastructureTypeFactory)
from geotrek.infrastructure.filters import SignageFilter, InfrastructureFilter


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


class InfrastructureViewsTest(MapEntityTest):
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
            'topology': '{"paths": [%s]}' % path.pk,
        }


class PointInfrastructureViewsTest(InfrastructureViewsTest):
    def get_good_data(self):
        PathFactory.create()
        return {
            'name': 'test',
            'description': 'oh',
            'structure': default_structure().pk,
            'type': InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.BUILDING).pk,
            'topology': '{"lat": 0.42, "lng": 0.666}'
        }


class SignageViewsTest(InfrastructureViewsTest):
    model = Signage
    modelfactory = SignageFactory

    def get_good_data(self):
        data = super(SignageViewsTest, self).get_good_data()
        data['type'] = InfrastructureTypeFactory.create(type=INFRASTRUCTURE_TYPES.SIGNAGE).pk
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


class InfraFilterTestMixin():

    factory = None
    filterset = None

    def test_intervention_filter(self):
        model = self.factory._associated_class

        user = PathManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

        # We will filter by this year
        year_idx, year = self.filterset.declared_filters['intervention_year'].get_choices()[1]
        good_date_year = datetime.datetime(year=year, month=2, day=2)
        bad_date_year = datetime.datetime(year=year + 2, month=2, day=2)

        # Bad topology/infrastructure: No intervention
        self.factory()

        # Bad signage: intervention with wrong year
        bad_topo = self.factory()
        InterventionFactory(topology=bad_topo, date=bad_date_year)

        # Good signage: intervention with the good year
        good_topo = self.factory()
        InterventionFactory(topology=good_topo, date=good_date_year)

        data = {
            'intervention_year': year_idx
        }
        response = self.client.get(model.get_jsonlist_url(), data)

        self.assertEqual(response.status_code, 200)
        topo_pk = simplejson.loads(response.content)['map_obj_pk']

        self.assertItemsEqual(topo_pk, [ good_topo.pk ])


class SignageFilterTest(InfraFilterTestMixin, TestCase):
    factory = SignageFactory
    filterset = SignageFilter


class InfrastructureFilterTest(InfraFilterTestMixin, TestCase):
    factory = InfrastructureFactory
    filterset = InfrastructureFilter
