# -*- coding: utf-8 -*-
from django.test import TestCase

from geotrek.common.tests import CommonTest
from geotrek.authent.tests import AuthentFixturesTest
from geotrek.authent.factories import PathManagerFactory
from geotrek.signage.models import Signage
from geotrek.core.factories import PathFactory
from geotrek.signage.factories import (SignageFactory, SignageTypeFactory,
                                       SignageNoPictogramFactory,
                                       InfrastructureConditionFactory)
from geotrek.signage.filters import SignageFilterSet
from geotrek.infrastructure.tests.test_views import InfraFilterTestMixin


class SignageTest(TestCase):
    def test_helpers(self):
        p = PathFactory.create()

        self.assertEquals(len(p.signages), 0)
        sign = SignageFactory.create(no_path=True)
        sign.add_path(path=p, start=0.5, end=0.5)

        self.assertItemsEqual(p.signages, [sign])


class SignageViewsTest(CommonTest):
    model = Signage
    modelfactory = SignageFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'name': 'test',
            'description': 'oh',
            'type': SignageTypeFactory.create().pk,
            'condition': InfrastructureConditionFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def test_description_in_detail_page(self):
        signa = SignageFactory.create(description="<b>Beautiful !</b>")
        self.login()
        response = self.client.get(signa.get_detail_url())
        self.assertContains(response, "<b>Beautiful !</b>")

    def test_check_structure_or_none_related_are_visible(self):
        self.login()
        signagetype = SignageTypeFactory.create(structure=None)
        response = self.client.get(self.model.get_add_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        form = response.context['form']
        type = form.fields['type']
        self.assertTrue((signagetype.pk, unicode(signagetype)) in type.choices)

    def test_no_pictogram(self):
        self.modelfactory = SignageNoPictogramFactory
        super(SignageViewsTest, self).test_api_detail_for_model()


class SignageFilterTest(InfraFilterTestMixin, AuthentFixturesTest):
    factory = SignageFactory
    filterset = SignageFilterSet

    def test_none_implantation_year_filter(self):

        self.login()
        model = self.factory._meta.model
        SignageFactory.create()
        response = self.client.get(model.get_list_url())
        self.assertFalse('option value="" selected>None</option' in str(response))

    def test_implantation_year_filter(self):
        filter = SignageFilterSet(data={'implantation_year': 2015})
        self.login()
        model = self.factory._meta.model
        i = SignageFactory.create(implantation_year=2015)
        i2 = SignageFactory.create(implantation_year=2016)
        response = self.client.get(model.get_list_url())

        self.assertTrue('<option value="2015">2015</option>' in str(response))
        self.assertTrue('<option value="2016">2016</option>' in str(response))

        self.assertTrue(i in filter.qs)
        self.assertFalse(i2 in filter.qs)

    def test_implantation_year_filter_with_str(self):
        filter = SignageFilterSet(data={'implantation_year': 'toto'})
        self.login()
        model = self.factory._meta.model
        i = SignageFactory.create(implantation_year=2015)
        i2 = SignageFactory.create(implantation_year=2016)
        response = self.client.get(model.get_list_url())

        self.assertTrue('<option value="2015">2015</option>' in str(response))
        self.assertTrue('<option value="2016">2016</option>' in str(response))

        self.assertIn(i, filter.qs)
        self.assertIn(i2, filter.qs)
