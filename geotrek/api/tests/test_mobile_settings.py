
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

    def test_settings_information_desk(self):
        self.client.login(username="administrator", password="administrator")
        informationdesk = tourism_factories.InformationDeskFactory()
        tourism_factories.InformationDeskFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(json_response.get('informationdesks')), InformationDesk.objects.count())
        self.assertEqual(json_response.get('informationdesks')[0].get('email'), informationdesk.email)
        self.assertEqual(json_response.get('informationdesks')[0].get('description'), informationdesk.description)

    def test_settings_network(self):
        self.client.login(username="administrator", password="administrator")
        network = trekking_factories.TrekNetworkFactory()
        trekking_factories.TrekNetworkFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(json_response.get('networks')), TrekNetwork.objects.count())
        self.assertEqual(json_response.get('networks')[0].get('label'), network.network)

    def test_settings_route(self):
        self.client.login(username="administrator", password="administrator")
        route = trekking_factories.RouteFactory()
        trekking_factories.RouteFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(json_response.get('routes')), Route.objects.count())
        self.assertEqual(json_response.get('routes')[0].get('label'), route.route)

    def test_settings_practice(self):
        self.client.login(username="administrator", password="administrator")
        practice = trekking_factories.PracticeFactory()
        trekking_factories.PracticeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(json_response.get('practices')), Practice.objects.count())
        self.assertEqual(json_response.get('practices')[0].get('label'), practice.name)
        self.assertIn(str(practice.pictogram), json_response.get('practices')[0].get('pictogram'))

    def test_settings_accessibility(self):
        self.client.login(username="administrator", password="administrator")
        accessibility = trekking_factories.AccessibilityFactory()
        trekking_factories.AccessibilityFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(json_response.get('accessibilities')), Accessibility.objects.count())
        self.assertEqual(json_response.get('accessibilities')[0].get('label'), accessibility.name)
        self.assertIn(str(accessibility.pictogram), json_response.get('accessibilities')[0].get('pictogram'))

    def test_settings_difficulty(self):
        self.client.login(username="administrator", password="administrator")
        difficulty = trekking_factories.DifficultyLevelFactory()
        trekking_factories.DifficultyLevelFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(json_response.get('difficulties')), DifficultyLevel.objects.count())
        self.assertEqual(json_response.get('difficulties')[0].get('label'), difficulty.difficulty)
        self.assertIn(str(difficulty.pictogram), json_response.get('difficulties')[0].get('pictogram'))

    def test_settings_theme(self):
        self.client.login(username="administrator", password="administrator")
        theme = common_factories.ThemeFactory()
        common_factories.ThemeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(json_response.get('themes')), Theme.objects.count())
        self.assertEqual(json_response.get('themes')[0].get('label'), theme.label)
        self.assertIn(str(theme.pictogram), json_response.get('themes')[0].get('pictogram'))

    def test_settings_city(self):
        self.client.login(username="administrator", password="administrator")
        city = zoning_factories.CityFactory()
        zoning_factories.CityFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(json_response.get('cities')), City.objects.count())
        self.assertEqual(json_response.get('cities')[0].get('name'), city.name)
        self.assertEqual(json_response.get('cities')[0].get('code'), city.code)
        self.assertEqual(json_response.get('cities')[0].get('lng'), city.geom.centroid.x)
        self.assertEqual(json_response.get('cities')[0].get('lat'), city.geom.centroid.y)
