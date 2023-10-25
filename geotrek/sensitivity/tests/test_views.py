from freezegun import freeze_time
import datetime
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from geotrek.authent.tests.factories import StructureFactory, UserProfileFactory
from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.trekking.tests.base import TrekkingManagerTest
from geotrek.common.tests import TranslationResetMixin
from geotrek.sensitivity.tests.factories import (
    SpeciesFactory,
    RegulatorySensitiveAreaFactory,
    SensitiveAreaFactory,
    MultiPolygonSensitiveAreaFactory
)
from geotrek.sensitivity.models import SportPractice
from geotrek.sensitivity.filters import SensitiveAreaFilterSet


class SensitiveAreaViewsSameStructureTests(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        cls.user = profile.user
        cls.user.user_permissions.add(Permission.objects.get(codename="add_sensitivearea"))
        cls.user.user_permissions.add(Permission.objects.get(codename="change_sensitivearea"))
        cls.user.user_permissions.add(Permission.objects.get(codename="delete_sensitivearea"))
        cls.user.user_permissions.add(Permission.objects.get(codename="read_sensitivearea"))
        cls.user.user_permissions.add(Permission.objects.get(codename="export_sensitivearea"))

        cls.area1 = SensitiveAreaFactory.create()
        structure = StructureFactory.create()
        cls.area2 = SensitiveAreaFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(user=self.user)

    def tearDown(self):
        self.client.logout()

    def test_can_edit_same_structure(self):
        url = reverse("sensitivity:sensitivearea_update", kwargs={"pk": self.area1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = reverse("sensitivity:sensitivearea_update", kwargs={"pk": self.area2.pk})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("sensitivity:sensitivearea_detail", kwargs={"pk": self.area2.pk}))

    def test_can_delete_same_structure(self):
        url = reverse("sensitivity:sensitivearea_delete", kwargs={"pk": self.area1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = reverse("sensitivity:sensitivearea_delete", kwargs={"pk": self.area2.pk})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("sensitivity:sensitivearea_detail", kwargs={"pk": self.area2.pk}))


class SensitiveAreaTemplatesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.area = SensitiveAreaFactory.create()

    def setUp(self):
        self.login()

    def login(self):
        user = User.objects.create_superuser('splash', 'splash@toto.com', password='booh')
        self.client.force_login(user=user)

    def tearDown(self):
        self.client.logout()

    def test_species_name_shown_in_detail_page(self):
        url = reverse("sensitivity:sensitivearea_detail", kwargs={"pk": self.area.pk})
        response = self.client.get(url)
        self.assertContains(response, self.area.species.name)


@freeze_time("2020-01-01")
class APIv2Test(TranslationResetMixin, TrekkingManagerTest):
    maxDiff = None

    def setUp(self):
        super().setUp()
        self.sensitivearea = SensitiveAreaFactory.create()
        self.species = self.sensitivearea.species
        self.pk = self.sensitivearea.pk
        self.expected_properties = {
            'create_datetime': self.sensitivearea.date_insert.isoformat().replace('+00:00', 'Z'),
            'update_datetime': self.sensitivearea.date_update.isoformat().replace('+00:00', 'Z'),
            'description': "Blabla",
            "elevation": None,
            'attachments': [],
            'contact': '<a href="mailto:toto@tata.com">toto@tata.com</a>',
            'kml_url': 'http://testserver/api/en/sensitiveareas/{pk}.kml'.format(pk=self.pk),
            'openair_url': 'http://testserver/api/en/sensitiveareas/{pk}/openair'.format(pk=self.pk),
            'info_url': self.species.url,
            'species_id': self.species.id,
            "name": self.species.name,
            "period": [False, False, False, False, False, True, True, False, False, False, False, False],
            'practices': [practice.pk for practice in self.species.practices.all()],
            'rules': [
                {'code': 'R1',
                 'description': None,
                 'id': self.sensitivearea.rules.all()[0].pk,
                 'name': 'Rule1',
                 'pictogram': 'http://testserver/media/picto_rule1.png',
                 'url': 'http://url.com'},
                {'code': 'R2',
                 'description': 'abcdefgh',
                 'id': self.sensitivearea.rules.all()[1].pk,
                 'name': 'Rule2',
                 'pictogram': 'http://testserver/media/picto_rule2.png',
                 'url': 'http://url.com'}],
            'provider': '',
            'structure': 'My structure',
            'published': True,
        }
        self.expected_geom = {
            'type': 'Polygon',
            'coordinates': [[
                [3.0, 46.5],
                [3.0, 46.500027],
                [3.0000391, 46.500027],
                [3.0000391, 46.5],
                [3.0, 46.5],
            ]],
        }
        self.expected_result = dict(self.expected_properties)
        self.expected_result['id'] = self.pk
        self.expected_result['geometry'] = self.expected_geom
        self.expected_result['url'] = 'http://testserver/api/v2/sensitivearea/{}/?format=json'.format(self.pk)
        self.expected_geo_result = {
            'bbox': [3.0, 46.5, 3.0000391, 46.500027],
            'geometry': self.expected_geom,
            'type': 'Feature',
            'id': self.pk,
            'properties': dict(self.expected_properties),
        }
        self.expected_geo_result['properties']['url'] = 'http://testserver/api/v2/sensitivearea/{}/?format=geojson'.format(self.pk)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_detail_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-detail', args=(self.pk,))
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertJSONEqual(response.content.decode(), self.expected_result)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_detail_sensitivearea_regulatory(self):
        self.sensitivearea = RegulatorySensitiveAreaFactory.create(species__period01=True)
        url = reverse('apiv2:sensitivearea-detail', args=(self.sensitivearea.pk,))
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertIsNone(response.json()['species_id'])

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_list_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertJSONEqual(response.content.decode(), {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [self.expected_result],
        })

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_geo_detail_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-detail', args=(self.pk,))
        params = {'format': 'geojson', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertJSONEqual(response.content.decode(), self.expected_geo_result)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_geo_list_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'geojson', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertJSONEqual(response.content.decode(), {
            'count': 1,
            'next': None,
            'previous': None,
            'type': 'FeatureCollection',
            'features': [self.expected_geo_result]
        })

    def test_no_duplicates_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'geojson', 'period': 'ignore', 'language': 'en'}
        params['practices'] = ','.join([str(p.pk) for p in self.species.practices.all()])
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1, response.json())

    def test_multipolygon(self):
        sensitivearea = MultiPolygonSensitiveAreaFactory.create()
        expected_geom = {
            'type': 'MultiPolygon',
            'coordinates': [
                [[
                    [3.0, 46.5],
                    [3.0, 46.500027],
                    [3.0000391, 46.500027],
                    [3.0000391, 46.5],
                    [3.0, 46.5],
                ]],
                [[
                    [3.0001304, 46.50009],
                    [3.0001304, 46.5001171],
                    [3.0001695, 46.5001171],
                    [3.0001695, 46.50009],
                    [3.0001304, 46.50009],
                ]]
            ],
        }
        url = reverse('apiv2:sensitivearea-detail', args=(sensitivearea.pk,))
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['geometry'], expected_geom)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_list_bubble_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': 'ignore', 'language': 'en', 'bubble': 'True'}
        response = self.client.get(url, params)
        self.expected_result[u'radius'] = None
        self.assertJSONEqual(response.content.decode(), {
            u'count': 1,
            u'previous': None,
            u'next': None,
            u'results': [self.expected_result],
        })

    def test_list_bubble_sensitivearea_with_point(self):
        sensitive_area_point = SensitiveAreaFactory.create(geom='SRID=2154;POINT (700040 6600040)',
                                                           species__period01=True, species__radius=5)
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'language': 'en', 'bubble': 'True', 'period': '1'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['radius'], 5)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_point.species.name)

    def test_list_sportpractice(self):
        url = reverse('apiv2:sportpractice-list')
        params = {'format': 'json', 'language': 'en'}
        response = self.client.get(url, params)
        sports_practice = SportPractice.objects.all()
        result_sportpractice = [{'id': sp.id, 'name': sp.name} for sp in sports_practice]
        self.assertJSONEqual(response.content.decode(), {
            u'count': 2,
            u'previous': None,
            u'next': None,
            u'results': result_sportpractice
        })

    def test_filters_structure(self):
        other_structure = StructureFactory.create(name='other')
        self.sensitivearea_other_structure = SensitiveAreaFactory.create(structure=other_structure)
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        params['structures'] = other_structure.pk
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], self.sensitivearea_other_structure.species.name)

    def test_filters_no_period(self):
        StructureFactory.create()
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 0)

    def test_filters_any_period(self):
        SensitiveAreaFactory.create()
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': 'any', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 2)

    def test_filters_specific_period(self):
        sensitive_area_jf = SensitiveAreaFactory.create(species__period01=True, species__period02=True)
        SensitiveAreaFactory.create(species__period01=True)
        SensitiveAreaFactory.create(species__period04=True)
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': '2,3', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_jf.species.name)

    def test_filters_no_period_get_month(self):
        sensitive_area_month = SensitiveAreaFactory.create(**{'species__period01': True})
        SensitiveAreaFactory.create(**{'species__period02': True})
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_month.species.name)


class SensitiveAreaOpenAirViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.area1 = SensitiveAreaFactory.create()
        cls.area2 = RegulatorySensitiveAreaFactory.create()
        cls.area3 = SensitiveAreaFactory.create(geom='POINT(700000 6600000)')
        species = SpeciesFactory(radius=100)
        cls.area4 = SensitiveAreaFactory.create(geom='POINT(700000 6600000)', species=species)

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice1",
        ]
    )
    @freeze_time("2020-01-01")
    def test_openair_detail(self):
        url = reverse("sensitivity:sensitivearea_openair_detail", args=("en", self.area4.pk))
        response = self.client.get(url, HTTP_HOST='testserver')
        self.assertEqual(response.status_code, 200)
        today = datetime.datetime.now().strftime('%d/%m/%Y')
        expected_response = b'* This file has been produced from GeoTrek sensitivity (https://geotrek.fr/) module from website http://testserver\n'
        '* Using pyopenair library (https://github.com/lpoaura/pyopenair)\n'
        '* This file was created on:  2020-01-01 00:00:00\n'
        '\n'
        'AC ZSM\n'
        'AN Species\n'
        f'*AUID GUId=! UId=! Id=(Identifiant-GeoTrek-sentivity) {self.area4.pk}\n'
        f'*ADescr Species (published on {today})\n'
        '*ATimes {"6": ["UTC(01/06->30/06)", "ANY(00:00->23:59)"],"7": ["UTC(01/07->31/07)", "ANY(00:00->23:59)"]}\n'
        'AH 329FT AGL\n'
        "AL SFC\n"
        'DP 46:29:59 N 03:00:04 E\n'
        'DP 46:29:56 N 03:00:00 E\n'
        'DP 46:29:59 N 02:59:55 E\n'
        'DP 46:30:03 N 03:00:00 E'
        self.assertContains(response, expected_response)

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice3",
        ]
    )
    @freeze_time("2020-01-01")
    def test_not_an_aerial_sensitiveaera_detail(self):
        url = reverse("sensitivity:sensitivearea_openair_detail", args=("en", self.area1.pk))
        response = self.client.get(url, HTTP_HOST='testserver')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'This is not an aerial area')

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice1",
        ]
    )
    @freeze_time("2020-01-01")
    def test_openair_list(self):
        url = reverse("sensitivity:sensitivearea_openair_list", args=("en",))
        response = self.client.get(url, HTTP_HOST='testserver')
        self.assertEqual(response.status_code, 200)
        expected_response = '* This file has been produced from GeoTrek sensitivity (https://geotrek.fr/) '
        'module from website http://testserver\n'
        '* Using pyopenair library (https://github.com/lpoaura/pyopenair)\n'
        '* This file was created on:  2020-01-01 00:00:00\n'
        '\n'
        'AC ZSM\n'
        self.assertContains(response, expected_response)


class SensitiveAreaFilterTest(TestCase):
    factory = SensitiveAreaFactory
    filterset = SensitiveAreaFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = SensitiveAreaFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        sensitive_area1 = SensitiveAreaFactory.create(provider='my_provider1')
        sensitive_area2 = SensitiveAreaFactory.create(provider='my_provider2')

        filter_set = SensitiveAreaFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(sensitive_area1, filter_set.qs)
        self.assertIn(sensitive_area2, filter_set.qs)
