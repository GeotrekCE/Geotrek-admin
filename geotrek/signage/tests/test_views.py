# -*- coding: utf-8 -*-
from collections import OrderedDict
import csv
from StringIO import StringIO

from django.test import TestCase
from django.utils import html
from django.utils.encoding import force_unicode

from geotrek.common.tests import CommonTest
from geotrek.authent.tests import AuthentFixturesTest
from geotrek.authent.factories import PathManagerFactory
from geotrek.signage.models import Signage, Blade
from geotrek.core.factories import PathFactory
from geotrek.signage.factories import (SignageFactory, SignageTypeFactory, BladeFactory, BladeTypeFactory,
                                       SignageNoPictogramFactory, BladeDirectionFactory, BladeColorFactory,
                                       InfrastructureConditionFactory, LineFactory)
from geotrek.signage.filters import SignageFilterSet
from geotrek.infrastructure.tests.test_views import InfraFilterTestMixin


class SignageTest(TestCase):
    def test_helpers(self):
        p = PathFactory.create()

        self.assertEquals(len(p.signages), 0)
        sign = SignageFactory.create(no_path=True)
        sign.add_path(path=p, start=0.5, end=0.5)

        self.assertItemsEqual(p.signages, [sign])


class BladeViewsTest(CommonTest):
    model = Blade
    modelfactory = BladeFactory
    userfactory = PathManagerFactory

    def get_bad_data(self):
        return OrderedDict([
            ('number', ''),
            ('lines-TOTAL_FORMS', '0'),
            ('lines-INITIAL_FORMS', '1'),
            ('lines-MAX_NUM_FORMS', '0'),
        ]), u'This field is required.'

    def get_good_data(self):
        return {
            'number': '1',
            'signage': SignageFactory.create().pk,
            'type': BladeTypeFactory.create().pk,
            'condition': InfrastructureConditionFactory.create().pk,
            'direction': BladeDirectionFactory.create().pk,
            'color': BladeColorFactory.create().pk,
            'topology': '{"lat": 5.1, "lng": 6.6}',
            'lines-TOTAL_FORMS': '2',
            'lines-INITIAL_FORMS': '0',
            'lines-MAX_NUM_FORMS': '1000',
            'lines-MIN_NUM_FORMS': '',

            'lines-0-number': "1",
            'lines-0-text': 'Text 0',
            'lines-0-distance': "10",
            'lines-0-pictogram_name': 'toto',
            'lines-0-time': '00:01:00',
            'lines-0-id': '',
            'lines-0-DELETE': '',

            'lines-1-number': "2",
            'lines-1-text': 'Text 1',
            'lines-1-distance': "0.2",
            'lines-1-pictogram_name': 'coucou',
            'lines-1-time': '00:00:10',
            'lines-1-id': '',
            'lines-1-DELETE': '',
        }

    def _post_add_form(self):
        signa = SignageFactory.create()
        self._post_form(self._get_add_url() + '?signage=%s' % signa.pk)

    def test_creation_form_on_signage(self):
        self.login()

        signa = SignageFactory.create()
        signage = u"%s" % signa

        response = self.client.get(Blade.get_add_url() + '?signage=%s' % signa.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, signage)
        form = response.context['form']
        self.assertEqual(form.initial['signage'], signa)
        # Should be able to save form successfully
        data = self.get_good_data()
        data['signage'] = signa.pk
        response = self.client.post(Blade.get_add_url() + '?signage=%s' % signa.pk, data)
        self.assertEqual(response.status_code, 302)

    def test_structure_is_set(self):
        self.login()

        signa = SignageFactory.create()

        response = self.client.post(self._get_add_url() + '?signage=%s' % signa.pk, self.get_good_data())
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.structure, self.user.profile.structure)

    def test_no_html_in_csv(self):
        self.login()

        blade = BladeFactory.create()
        LineFactory.create(blade=blade)
        fmt = 'csv'
        response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')


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

    def test_no_html_in_csv(self):
        if self.model is None:
            return  # Abstract test should not run

        self.login()

        self.modelfactory.create()

        fmt = 'csv'
        response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')

        # Read the csv
        lines = list(csv.reader(StringIO(response.content), delimiter=','))
        # There should be one more line in the csv than in the items: this is the header line
        self.assertEqual(len(lines), self.model.objects.all().count() + 1)

        for line in lines:
            for col in line:
                # the col should not contains any html tags
                self.assertEquals(force_unicode(col), html.strip_tags(force_unicode(col)))


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
