from freezegun import freeze_time

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.authent.tests.factories import StructureFactory, UserProfileFactory
from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.trekking.tests.base import TrekkingManagerTest
from geotrek.common.tests import TranslationResetMixin
from geotrek.sensitivity.tests.factories import RegulatorySensitiveAreaFactory, SensitiveAreaFactory, MultiPolygonSensitiveAreaFactory
from geotrek.sensitivity.models import SportPractice


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
        url = "/sensitivearea/edit/{pk}/".format(pk=self.area1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = "/sensitivearea/edit/{pk}/".format(pk=self.area2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/sensitivearea/{pk}/".format(pk=self.area2.pk))

    def test_can_delete_same_structure(self):
        url = "/sensitivearea/delete/{pk}/".format(pk=self.area1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = "/sensitivearea/delete/{pk}/".format(pk=self.area2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/sensitivearea/{pk}/".format(pk=self.area2.pk))


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
        url = "/sensitivearea/{pk}/".format(pk=self.area.pk)
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
            'contact': '<a href="mailto:toto@tata.com">toto@tata.com</a>',
            'kml_url': 'http://testserver/api/en/sensitiveareas/{pk}.kml'.format(pk=self.pk),
            'openair_url': 'http://testserver/api/en/sensitiveareas/{pk}/openair'.format(pk=self.pk),
            'info_url': self.species.url,
            'species_id': self.species.id,
            "name": self.species.name,
            "period": [False, False, False, False, False, True, True, False, False, False, False, False],
            'practices': [p.pk for p in self.species.practices.all()],
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

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES = ['Practice1', ])
    def test_detail_sensitivearea(self):
        url = '/api/v2/sensitivearea/{pk}/?format=json&period=ignore&language=en'.format(pk=self.pk)
        response = self.client.get(url)
        self.assertJSONEqual(response.content.decode(), self.expected_result)
    
    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES = ['Practice1', ])
    def test_detail_sensitivearea_regulatory(self):
        self.sensitivearea = RegulatorySensitiveAreaFactory.create(species__period01=True)
        url = '/api/v2/sensitivearea/{pk}/?format=json&period=ignore&language=en'.format(pk=self.sensitivearea.pk)
        response = self.client.get(url)
        self.assertIsNone(response.json()['species_id'])

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES = ['Practice1', ])
    def test_list_sensitivearea(self):
        url = '/api/v2/sensitivearea/?format=json&period=ignore&language=en'
        response = self.client.get(url)
        self.assertJSONEqual(response.content.decode(), {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [self.expected_result],
        })

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES = ['Practice1', ])
    def test_geo_detail_sensitivearea(self):
        url = '/api/v2/sensitivearea/{pk}/?format=geojson&period=ignore&language=en'.format(pk=self.pk)
        response = self.client.get(url)
        self.assertJSONEqual(response.content.decode(), self.expected_geo_result)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES = ['Practice1', ])
    def test_geo_list_sensitivearea(self):
        url = '/api/v2/sensitivearea/?format=geojson&period=ignore&language=en'
        response = self.client.get(url)
        self.assertJSONEqual(response.content.decode(), {
            'count': 1,
            'next': None,
            'previous': None,
            'type': 'FeatureCollection',
            'features': [self.expected_geo_result]
        })

    def test_no_duplicates_sensitivearea(self):
        url = '/api/v2/sensitivearea/?format=geojson&period=ignore&language=en&practices={}'.format(
            ','.join([str(p.pk) for p in self.species.practices.all()])
        )
        response = self.client.get(url)
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
        url = '/api/v2/sensitivearea/{pk}/?format=json&period=ignore&language=en'.format(pk=sensitivearea.pk)
        response = self.client.get(url)
        self.assertEqual(response.json()['geometry'], expected_geom)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES = ['Practice1', ])
    def test_list_bubble_sensitivearea(self):
        url = '/api/v2/sensitivearea/?format=json&period=ignore&language=en&bubble=True'
        response = self.client.get(url)
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
        url = '/api/v2/sensitivearea/?format=json&period=ignore&language=en&bubble=True&period=1'
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['radius'], 5)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_point.species.name)

    def test_list_sportpractice(self):
        url = '/api/v2/sensitivearea_practice/?format=json&language=en'
        response = self.client.get(url)
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
        url = '/api/v2/sensitivearea/?format=json&language=en&period=ignore&structures={}'.format(other_structure.pk)
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], self.sensitivearea_other_structure.species.name)

    def test_filters_no_period(self):
        StructureFactory.create()
        url = '/api/v2/sensitivearea/?format=json&language=en'
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 0)

    def test_filters_any_period(self):
        SensitiveAreaFactory.create()
        url = '/api/v2/sensitivearea/?format=json&language=en&period=any'
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 2)

    def test_filters_specific_period(self):
        sensitive_area_jf = SensitiveAreaFactory.create(species__period01=True, species__period02=True)
        SensitiveAreaFactory.create(species__period01=True)
        SensitiveAreaFactory.create(species__period04=True)
        url = '/api/v2/sensitivearea/?format=json&language=en&period=2,3'
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_jf.species.name)

    def test_filters_no_period_get_month(self):
        sensitive_area_month = SensitiveAreaFactory.create(**{'species__period01': True})
        SensitiveAreaFactory.create(**{'species__period02': True})
        url = '/api/v2/sensitivearea/?format=json&language=en'
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_month.species.name)
