from collections import OrderedDict
import csv
from io import StringIO
import json

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import gettext

from geotrek.common.tests import CommonTest, GeotrekAPITestCase
from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import PathManagerFactory, StructureFactory
from geotrek.common.tests.factories import OrganismFactory
from geotrek.signage.models import Signage, Blade
from geotrek.core.tests.factories import PathFactory
from geotrek.signage.tests.factories import (SignageFactory, SignageTypeFactory, BladeFactory, BladeTypeFactory,
                                             SignageNoPictogramFactory, BladeDirectionFactory, BladeColorFactory,
                                             InfrastructureConditionFactory, LineFactory, LineDirectionFactory)
from geotrek.signage.filters import BladeFilterSet, SignageFilterSet
from geotrek.infrastructure.tests.test_filters import InfraFilterTestMixin

from mapentity.tests.factories import SuperUserFactory


class SignageTest(TestCase):
    def test_helpers(self):
        p = PathFactory.create()

        self.assertEqual(len(p.signages), 0)
        if settings.TREKKING_TOPOLOGY_ENABLED:
            sign = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        else:
            sign = SignageFactory.create(geom='SRID=2154;POINT (700050 6600050)')

        self.assertCountEqual(p.signages, [sign])


class SignageTemplatesTest(TestCase):

    def setUp(self):
        self.login()

    def login(self):
        user = User.objects.create_superuser('test', 'test@example.com', password='test')
        self.client.force_login(user=user)

    def tearDown(self):
        self.client.logout()

    @override_settings(DIRECTION_ON_LINES_ENABLED=True)
    def test_direction_field_on_each_line_on_detail_page_when_direction_on_lines_enabled(self):
        line_1 = LineFactory.create(
            number=2,
            direction=LineDirectionFactory.create(label="A direction on the line 1")
        )
        line_2 = LineFactory.create(
            number=3,
            direction=LineDirectionFactory.create(label="A direction on the line 2")
        )
        blade = BladeFactory.create(
            direction=BladeDirectionFactory.create(label="A direction on the blade"),
        )
        blade.lines.add(line_1, line_2)

        response = self.client.get(blade.signage.get_detail_url())

        self.assertNotContains(response, "A direction on the blade")
        self.assertContains(response, gettext("Direction"))
        self.assertContains(response, "A direction on the line 1")
        self.assertContains(response, "A direction on the line 2")


class BladeViewsTest(GeotrekAPITestCase, CommonTest):
    model = Blade
    modelfactory = BladeFactory
    userfactory = PathManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [3.0, 46.5]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'number', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'type', 'eid']

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

    def get_expected_json_attrs(self):
        return {
            'color': self.obj.color.pk,
            'condition': self.obj.condition.pk,
            'direction': self.obj.direction.pk,
            'number': '1',
            'order_lines': [self.obj.lines.get().pk],
            'structure': {'id': self.obj.structure.pk, 'name': 'My structure'},
            'type': {
                'label': 'Blade type'
            }
        }

    def get_expected_datatables_attrs(self):
        return {
            'color': self.obj.color.label,
            'direction': self.obj.direction.label,
            'id': self.obj.pk,
            'number': self.obj.number_display,
            'type': self.obj.type.label
        }

    def get_bad_data(self):
        return OrderedDict([
            ('number', ''),
            ('lines-TOTAL_FORMS', '0'),
            ('lines-INITIAL_FORMS', '1'),
            ('lines-MAX_NUM_FORMS', '0'),
        ]), 'This field is required.'

    def get_good_data(self):
        good_data = {
            'number': '2',
            'type': BladeTypeFactory.create().pk,
            'condition': InfrastructureConditionFactory.create().pk,
            'direction': BladeDirectionFactory.create().pk,
            'color': BladeColorFactory.create().pk,
            'lines-TOTAL_FORMS': '2',
            'lines-INITIAL_FORMS': '0',
            'lines-MAX_NUM_FORMS': '1000',
            'lines-MIN_NUM_FORMS': '',

            'lines-0-number': "2",
            'lines-0-text': 'Text 0',
            'lines-0-distance': "10",
            'lines-0-pictogram_name': 'toto',
            'lines-0-time': '00:01:00',
            'lines-0-id': '',
            'lines-0-DELETE': '',

            'lines-1-number': "3",
            'lines-1-text': 'Text 1',
            'lines-1-distance': "0.2",
            'lines-1-pictogram_name': 'coucou',
            'lines-1-time': '00:00:10',
            'lines-1-id': '',
            'lines-1-DELETE': '',
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            signage = SignageFactory.create()
            good_data['topology'] = '{"lat": 5.1, "lng": 6.6}'
            good_data['signage'] = signage.pk
        else:
            signage = SignageFactory.create(geom='SRID=2154;POINT(5.1 6.6)')
            good_data['signage'] = signage.pk
            good_data['topology'] = signage.geom.ewkt
        return good_data

    def _post_add_form(self):
        signa = SignageFactory.create()
        self._post_form(self._get_add_url() + '?signage=%s' % signa.pk)

    def _check_update_geom_permission(self, response):
        if self.user.has_perm('{app}.change_geom_{model}'.format(app=self.model._meta.app_label,
                                                                 model=self.model._meta.model_name)) and \
                settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertContains(response, '.modifiable = true;')
        else:
            self.assertContains(response, '.modifiable = false;')

    def test_creation_form_on_signage(self):
        signa = SignageFactory.create()
        signage = "%s" % signa

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

    def test_delete_redirection(self):
        signage = SignageFactory.create()
        blade = BladeFactory.create(signage=signage)

        response = self.client.post(Blade.get_delete_url(blade))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, signage.get_detail_url(), status_code=302)

    def test_structure_is_set(self):
        signa = SignageFactory.create()

        response = self.client.post(self._get_add_url() + '?signage=%s' % signa.pk, self.get_good_data())
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.structure, self.user.profile.structure)

    def test_basic_format_not_ascii(self):
        signage = SignageFactory.create(name="ééé")
        BladeFactory.create(signage=signage)
        for fmt in ('csv', 'shp', 'gpx'):
            response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
            self.assertEqual(response.status_code, 200, "")

    def test_csv_format_with_lines(self):
        signage = SignageFactory.create(name="ééé")
        blade = BladeFactory.create(signage=signage)
        blade.lines.all().delete()
        LineFactory.create(blade=blade, number=3)
        LineFactory.create(blade=blade, number=2)
        response = self.client.get(self.model.get_format_list_url() + '?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.split(b'\r\n')[0], b"ID,City,Signage,Printed elevation,Code,Type,Color,"
                                                             b"Direction,Condition,"
                                                             b"Coordinates (WGS 84 / Pseudo-Mercator),"
                                                             b"Number 1,Text 1,"
                                                             b"Distance 1,Time 1,Pictograms 1,"
                                                             b"Number 2,Text 2,"
                                                             b"Distance 2,Time 2,Pictograms 2")

    def test_set_structure_with_permission(self):
        # The structure do not change because it changes with the signage form.
        # Need to check blade structure and line
        perm = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm)
        structure = StructureFactory()
        self.assertNotEqual(structure, self.user.profile.structure)
        signage = SignageFactory(structure=structure)
        data = self.get_good_data()
        data['signage'] = signage.pk
        data['structure'] = self.user.profile.structure.pk
        response = self.client.post('%s?signage=%s' % (Blade.get_add_url(), signage.pk), data)
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.signage.structure, structure)

    def test_structure_is_not_changed_without_permission(self):
        structure = StructureFactory()
        self.assertNotEqual(structure, self.user.profile.structure)
        self.assertFalse(self.user.has_perm('authent.can_bypass_structure'))
        obj = self.modelfactory.create(signage__structure=structure)
        result = self.client.post(obj.get_update_url(), self.get_good_data())
        self.assertEqual(result.status_code, 302)
        self.assertEqual(self.model.objects.first().structure, structure)

    @override_settings(DIRECTION_ON_LINES_ENABLED=True)
    def test_direction_field_is_hidden_on_blade_list_when_direction_on_lines_enabled(self):
        BladeFactory.create()

        response = self.client.get(Blade.get_datatablelist_url())

        data = json.loads(response.content)
        blade_repr = data['data'][0]
        self.assertNotIn('direction', blade_repr)

    @override_settings(DIRECTION_ON_LINES_ENABLED=True, COLUMNS_LISTS={'blade_view': ['direction', 'condition']})
    def test_direction_custom_field_is_hidden_on_blade_list_when_direction_on_lines_enabled(self):
        BladeFactory.create()

        response = self.client.get(Blade.get_datatablelist_url())

        data = json.loads(response.content)
        blade_repr = data['data'][0]
        self.assertNotIn('direction', blade_repr)
        self.assertIn('condition', blade_repr)

    def test_direction_field_visibility_on_blade_csv_format(self):
        BladeFactory.create()

        response = self.client.get(Blade.get_format_list_url() + '?format=csv')

        lines = list(csv.reader(StringIO(response.content.decode("utf-8")), delimiter=','))
        self.assertIn('Direction', lines[0])
        self.assertIn('Blade direction', lines[1])
        self.assertNotIn('Direction 1', lines[0])
        self.assertNotIn('Line direction', lines[1])

    @override_settings(DIRECTION_ON_LINES_ENABLED=True)
    def test_direction_field_visibility_on_blade_csv_format_when_direction_on_lines_enabled(self):
        BladeFactory.create()

        response = self.client.get(Blade.get_format_list_url() + '?format=csv')

        lines = list(csv.reader(StringIO(response.content.decode("utf-8")), delimiter=','))
        self.assertNotIn('Direction', lines[0])
        self.assertNotIn('Blade direction', lines[1])
        self.assertIn('Direction 1', lines[0])
        self.assertIn('Line direction', lines[1])


class BladeTemplatesTest(TestCase):

    def setUp(self):
        self.login()

    def login(self):
        user = User.objects.create_superuser('test', 'test@example.com', password='test')
        self.client.force_login(user=user)

    def tearDown(self):
        self.client.logout()

    def test_direction_field_visibility_on_detail_page(self):
        blade = BladeFactory.create(
            direction=BladeDirectionFactory.create(label="A direction on the blade")
        )
        line = blade.lines.first()
        line.direction = BladeDirectionFactory.create(label="A direction on the line")
        line.save()

        response = self.client.get(blade.get_detail_url())

        self.assertContains(response, "A direction on the blade")
        self.assertNotContains(response, "A direction on the line")

    @override_settings(DIRECTION_ON_LINES_ENABLED=True)
    def test_direction_field_visibility_on_detail_page_when_direction_on_lines_enabled(self):
        blade = BladeFactory.create(
            direction=BladeDirectionFactory.create(label="A direction on the blade")
        )
        line = blade.lines.first()
        line.direction = BladeDirectionFactory.create(label="A direction on the line")
        line.save()

        response = self.client.get(blade.get_detail_url())

        self.assertNotContains(response, "A direction on the blade")
        self.assertContains(response, "A direction on the line")


class SignageViewsTest(GeotrekAPITestCase, CommonTest):
    model = Signage
    modelfactory = SignageFactory
    userfactory = PathManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [3.0, 46.5]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'name', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'type', 'eid']

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

    def get_expected_json_attrs(self):
        return {
            'code': '',
            'condition': self.obj.condition.pk,
            'manager': self.obj.manager.pk,
            'name': 'Signage',
            'printed_elevation': 4807,
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False}
            ],
            'sealing': self.obj.sealing.pk,
            'structure': {'id': self.obj.structure.pk, 'name': 'My structure'},
            'type': {
                'id': self.obj.type.pk,
                'label': 'Signage type',
                'pictogram': '/media/upload/signage_type.png',
            },
        }

    def get_expected_datatables_attrs(self):
        return {
            'code': self.obj.code,
            'condition': self.obj.condition.label,
            'id': self.obj.pk,
            'name': self.obj.name_display,
            'type': self.obj.type.label
        }

    def get_good_data(self):
        good_data = {
            'name_fr': 'test',
            'name_en': 'test_en',
            'description_fr': 'oh',
            'publication_date': '2020-03-17',
            'type': SignageTypeFactory.create().pk,
            'condition': InfrastructureConditionFactory.create().pk,
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data['topology'] = '{"paths": [%s]}' % path.pk
        else:
            good_data['geom'] = 'POINT(0.42 0.666)'
        return good_data

    def test_content_in_detail_page(self):
        signa = SignageFactory.create(description="<b>Beautiful !</b>")
        response = self.client.get(signa.get_detail_url())
        self.assertContains(response, "<b>Beautiful !</b>")
        self.assertContains(response, "(WGS 84 / Pseudo-Mercator)")

    def test_check_structure_or_none_related_are_visible(self):
        signagetype = SignageTypeFactory.create(structure=None)
        response = self.client.get(self.model.get_add_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        form = response.context['form']
        type = form.fields['type']
        self.assertTrue((signagetype.pk, str(signagetype)) in type.choices)

    def test_no_pictogram(self):
        self.obj = SignageNoPictogramFactory.create(publication_date='2020-03-17')
        response = self.client.get('/api/en/signages/{}'.format(self.obj.pk))
        self.assertEqual(response.status_code, 200)
        expected_json_attrs = {'id': self.obj.pk, **self.get_expected_json_attrs()}
        expected_json_attrs['type']['pictogram'] = '/static/signage/picto-signage.png'
        self.assertJSONEqual(response.content, expected_json_attrs)


class SignageFilterTest(InfraFilterTestMixin, AuthentFixturesTest):
    factory = SignageFactory
    filterset = SignageFilterSet

    def test_none_implantation_year_filter(self):

        self.login()
        model = self.factory._meta.model
        SignageFactory.create()
        response = self.client.get(model.get_list_url())
        self.assertNotContains(response, 'option value="" selected>None</option')

    def test_implantation_year_filter(self):
        self.login()
        model = self.factory._meta.model
        i = SignageFactory.create(implantation_year=2015)
        i2 = SignageFactory.create(implantation_year=2016)
        response = self.client.get(model.get_list_url())

        self.assertContains(response, '<option value="2015">2015</option>')
        self.assertContains(response, '<option value="2016">2016</option>')

        filter = SignageFilterSet(data={'implantation_year': [2015]})
        self.assertTrue(i in filter.qs)
        self.assertFalse(i2 in filter.qs)

    def test_implantation_year_filter_with_str(self):
        i = SignageFactory.create(implantation_year=2015)
        i2 = SignageFactory.create(implantation_year=2016)
        filter_set = SignageFilterSet(data={'implantation_year': 'toto'})
        filter_form = filter.form

        self.assertIn('<option value="2015">2015</option>', filter_form.as_p())
        self.assertIn('<option value="2016">2016</option>', filter_form.as_p())

        self.assertIn(i, filter_set.qs)
        self.assertIn(i2, filter_set.qs)


class BladeFilterSetTest(TestCase):
    factory = BladeFactory
    filterset = BladeFilterSet

    @classmethod
    def setUpTestData(cls):
        cls.model = cls.factory._meta.model
        cls.user = SuperUserFactory.create()

        cls.manager = OrganismFactory()
        cls.manager2 = OrganismFactory()

        cls.signage = SignageFactory(manager=cls.manager, code="COUCOU")
        cls.signage2 = SignageFactory(manager=cls.manager2, code="ADIEU")

        cls.blade = cls.factory(signage=cls.signage)
        cls.blade2 = cls.factory(signage=cls.signage2)

    def setUp(self):
        self.client.force_login(self.user)

    def test_filter_by_organism(self):
        filter = BladeFilterSet(data={'manager': [self.manager.pk,]})
        response = self.client.get(self.model.get_list_url())

        self.assertEqual(response.status_code, 200)

        self.assertIn(self.blade, filter.qs)
        self.assertNotIn(self.blade2, filter.qs)
