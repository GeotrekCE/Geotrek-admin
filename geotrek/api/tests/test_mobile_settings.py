from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from geotrek.common import factories as common_factories
from geotrek.common.models import Theme
from geotrek.trekking import factories as trekking_factories
from geotrek.trekking.models import TrekNetwork, Route, Practice, Accessibility, DifficultyLevel
from geotrek.tourism import factories as tourism_factories
from geotrek.tourism.models import InformationDeskType
from geotrek.zoning import factories as zoning_factories
from geotrek.zoning.models import City


SETTINGS_STRUCTURE = sorted([
    'filters', 'data'
])

SETTINGS_DATA_STRUCTURE = sorted([
    'information_desk_types', 'networks', 'route', 'practice', 'accessibilities', 'difficulty', 'themes', 'cities',
    'length', 'duration', 'poi_types', 'touristiccontent_categories', 'touristiccontent_types', 'touristicevent_types',
    'ascent', 'districts'
])


class SettingsMobileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrator = User.objects.create(username="administrator", is_superuser=True,
                                                is_staff=True, is_active=True)
        cls.administrator.set_password('administrator')
        cls.administrator.save()
        cls.administrator.refresh_from_db()

    def get_settings(self, params=None):
        return self.client.get(reverse('apimobile:settings'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def test_settings_structure(self):
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         SETTINGS_STRUCTURE)
        values_data = [values.get('id') for values in json_response.get('data')]
        self.assertEqual(sorted(values_data),
                         SETTINGS_DATA_STRUCTURE)

    def test_settings_information_desk(self):
        informationdesktype = tourism_factories.InformationDeskTypeFactory()
        tourism_factories.InformationDeskTypeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        informationdesk_item = next((item.get('values') for item in json_response.get('data')
                                     if item['id'] == 'information_desk_types'), None)

        self.assertEqual(len(informationdesk_item), InformationDeskType.objects.count())
        self.assertEqual(informationdesk_item[0].get('name'), informationdesktype.label)
        self.assertIn(str(informationdesktype.pictogram), informationdesk_item[0].get('pictogram'))

    def test_settings_network(self):
        network = trekking_factories.TrekNetworkFactory()
        trekking_factories.TrekNetworkFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        network_item = next((item.get('values') for item in json_response.get('data')
                             if item['id'] == 'networks'), None)
        self.assertEqual(len(network_item), TrekNetwork.objects.count())
        self.assertEqual(network_item[0].get('name'), network.network)
        self.assertIn(str(network.pictogram), network_item[0].get('pictogram'))

    def test_settings_route(self):
        route = trekking_factories.RouteFactory()
        trekking_factories.RouteFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        route_item = next((item.get('values') for item in json_response.get('data')
                           if item['id'] == 'route'), None)

        self.assertEqual(len(route_item), Route.objects.count())
        self.assertEqual(route_item[0].get('name'), route.route)
        self.assertIn(str(route.pictogram), route_item[0].get('pictogram'))

    def test_settings_route_no_picto(self):
        route = trekking_factories.RouteFactory(pictogram=None)
        trekking_factories.RouteFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        route_item = next((item.get('values') for item in json_response.get('data')
                           if item['id'] == 'route'), None)

        self.assertEqual(len(route_item), Route.objects.count())
        self.assertEqual(route_item[0].get('name'), route.route)
        self.assertEqual(None, route_item[0].get('pictogram'))

    def test_settings_practice(self):
        practice = trekking_factories.PracticeFactory()
        trekking_factories.PracticeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        practice_item = next((item.get('values') for item in json_response.get('data')
                              if item['id'] == 'practice'), None)
        self.assertEqual(len(practice_item), Practice.objects.count())
        self.assertEqual(practice_item[0].get('name'), practice.name)
        self.assertIn(str(practice.pictogram), practice_item[0].get('pictogram'))

    def test_settings_accessibility(self):
        accessibility = trekking_factories.AccessibilityFactory()
        trekking_factories.AccessibilityFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        accessibility_item = next((item.get('values') for item in json_response.get('data')
                                   if item['id'] == 'accessibilities'), None)
        self.assertEqual(len(accessibility_item), Accessibility.objects.count())
        self.assertEqual(accessibility_item[0].get('name'), accessibility.name)
        self.assertIn(str(accessibility.pictogram), accessibility_item[0].get('pictogram'))

    def test_settings_accessibility_no_picto(self):
        accessibility = trekking_factories.AccessibilityFactory(pictogram=None)
        trekking_factories.AccessibilityFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        accessibility_item = next((item.get('values') for item in json_response.get('data')
                                   if item['id'] == 'accessibilities'), None)
        self.assertEqual(len(accessibility_item), Accessibility.objects.count())
        self.assertEqual(accessibility_item[0].get('name'), accessibility.name)
        self.assertEqual(None, accessibility_item[0].get('pictogram'))

    def test_settings_difficulty(self):
        difficulty = trekking_factories.DifficultyLevelFactory()
        trekking_factories.DifficultyLevelFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        difficulty_item = next((item.get('values') for item in json_response.get('data')
                                if item['id'] == 'difficulty'), None)
        self.assertEqual(len(difficulty_item), DifficultyLevel.objects.count())
        self.assertEqual(difficulty_item[0].get('name'), difficulty.difficulty)
        self.assertIn(str(difficulty.pictogram), difficulty_item[0].get('pictogram'))

    def test_settings_difficulty_no_picto(self):
        difficulty = trekking_factories.DifficultyLevelFactory(pictogram=None)
        trekking_factories.DifficultyLevelFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        difficulty_item = next((item.get('values') for item in json_response.get('data')
                                if item['id'] == 'difficulty'), None)
        self.assertEqual(len(difficulty_item), DifficultyLevel.objects.count())
        self.assertEqual(difficulty_item[0].get('name'), difficulty.difficulty)
        self.assertEqual(None, difficulty_item[0].get('pictogram'))

    def test_settings_theme(self):
        theme = common_factories.ThemeFactory()
        common_factories.ThemeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        theme_item = next((item.get('values') for item in json_response.get('data')
                           if item['id'] == 'themes'), None)
        self.assertEqual(len(theme_item), Theme.objects.count())
        self.assertEqual(theme_item[0].get('name'), theme.label)
        self.assertIn(str(theme.pictogram), theme_item[0].get('pictogram'))

    def test_settings_city(self):
        city = zoning_factories.CityFactory()
        zoning_factories.CityFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        city_item = next((item.get('values') for item in json_response.get('data')
                          if item['id'] == 'cities'), None)
        self.assertEqual(len(city_item), City.objects.count())
        self.assertEqual(city_item[0].get('name'), city.name)
        self.assertEqual(city_item[0].get('id'), city.code)
