
from __future__ import unicode_literals

import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from geotrek.common import factories as common_factories
from geotrek.common.models import Theme
from geotrek.trekking import factories as trekking_factories
from geotrek.trekking.models import TrekNetwork, Route, Practice, Accessibility, DifficultyLevel
from geotrek.tourism import factories as tourism_factories
from geotrek.tourism.models import InformationDesk
from geotrek.zoning import factories as zoning_factories
from geotrek.zoning.models import City


SETTINGS_STRUCTURE = sorted([
    'filters', 'data'
])

SETTINGS_DATA_STRUCTURE = sorted([
    'informationdesks', 'networks', 'routes', 'practices', 'accessibilities', 'difficulties', 'themes', 'cities'
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

    def test_settings_no_permission(self):
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 401)

    def test_settings_structure(self):
        self.client.login(username="administrator", password="administrator")

        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(json_response.keys()),
                         SETTINGS_STRUCTURE)
        values_data = [values.get('id') for values in json_response.get('data')]
        self.assertEqual(sorted(values_data),
                         SETTINGS_DATA_STRUCTURE)

    def test_settings_information_desk(self):
        self.client.login(username="administrator", password="administrator")
        informationdesk = tourism_factories.InformationDeskFactory()
        tourism_factories.InformationDeskFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        informationdesk_item = next((item.get('values') for item in json_response.get('data')
                                     if item['id'] == 'informationdesks'), None)

        self.assertEqual(len(informationdesk_item), InformationDesk.objects.count())
        self.assertEqual(informationdesk_item[0].get('email'), informationdesk.email)
        self.assertEqual(informationdesk_item[0].get('description'), informationdesk.description)

    def test_settings_network(self):
        self.client.login(username="administrator", password="administrator")
        network = trekking_factories.TrekNetworkFactory()
        trekking_factories.TrekNetworkFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        network_item = next((item.get('values') for item in json_response.get('data')
                             if item['id'] == 'networks'), None)
        self.assertEqual(len(network_item), TrekNetwork.objects.count())
        self.assertEqual(network_item[0].get('label'), network.network)

    def test_settings_route(self):
        self.client.login(username="administrator", password="administrator")
        route = trekking_factories.RouteFactory()
        trekking_factories.RouteFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        route_item = next((item.get('values') for item in json_response.get('data')
                           if item['id'] == 'routes'), None)

        self.assertEqual(len(route_item), Route.objects.count())
        self.assertEqual(route_item[0].get('label'), route.route)

    def test_settings_practice(self):
        self.client.login(username="administrator", password="administrator")
        practice = trekking_factories.PracticeFactory()
        trekking_factories.PracticeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        practice_item = next((item.get('values') for item in json_response.get('data')
                              if item['id'] == 'practices'), None)
        self.assertEqual(len(practice_item), Practice.objects.count())
        self.assertEqual(practice_item[0].get('label'), practice.name)
        self.assertIn(str(practice.pictogram), practice_item[0].get('pictogram'))

    def test_settings_accessibility(self):
        self.client.login(username="administrator", password="administrator")
        accessibility = trekking_factories.AccessibilityFactory()
        trekking_factories.AccessibilityFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        accessibility_item = next((item.get('values') for item in json_response.get('data')
                                   if item['id'] == 'accessibilities'), None)
        self.assertEqual(len(accessibility_item), Accessibility.objects.count())
        self.assertEqual(accessibility_item[0].get('label'), accessibility.name)
        self.assertIn(str(accessibility.pictogram), accessibility_item[0].get('pictogram'))

    def test_settings_difficulty(self):
        self.client.login(username="administrator", password="administrator")
        difficulty = trekking_factories.DifficultyLevelFactory()
        trekking_factories.DifficultyLevelFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        difficulty_item = next((item.get('values') for item in json_response.get('data')
                                if item['id'] == 'difficulties'), None)
        self.assertEqual(len(difficulty_item), DifficultyLevel.objects.count())
        self.assertEqual(difficulty_item[0].get('label'), difficulty.difficulty)
        self.assertIn(str(difficulty.pictogram), difficulty_item[0].get('pictogram'))

    def test_settings_theme(self):
        self.client.login(username="administrator", password="administrator")
        theme = common_factories.ThemeFactory()
        common_factories.ThemeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        theme_item = next((item.get('values') for item in json_response.get('data')
                           if item['id'] == 'themes'), None)
        self.assertEqual(len(theme_item), Theme.objects.count())
        self.assertEqual(theme_item[0].get('label'), theme.label)
        self.assertIn(str(theme.pictogram), theme_item[0].get('pictogram'))

    def test_settings_city(self):
        self.client.login(username="administrator", password="administrator")
        city = zoning_factories.CityFactory()
        zoning_factories.CityFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        city_item = next((item.get('values') for item in json_response.get('data')
                          if item['id'] == 'cities'), None)
        self.assertEqual(len(city_item), City.objects.count())
        self.assertEqual(city_item[0].get('name'), city.name)
        self.assertEqual(city_item[0].get('code'), city.code)
