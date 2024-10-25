from django.urls import reverse
from django.test.testcases import TestCase

from geotrek.common.tests import factories as common_factories
from geotrek.trekking.tests import factories as trekking_factories
from geotrek.trekking.models import POIType
from geotrek.tourism.tests import factories as tourism_factories
from geotrek.tourism.models import TouristicContentType, TouristicContentCategory, TouristicEventType
from geotrek.zoning.tests import factories as zoning_factories
from geotrek.zoning.models import City, District


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
        cls.accessibility_1 = trekking_factories.AccessibilityFactory.create()
        cls.accessibility_2 = trekking_factories.AccessibilityFactory.create()
        cls.difficulty = trekking_factories.DifficultyLevelFactory.create()
        cls.trek_network = trekking_factories.TrekNetworkFactory.create(network="TEST")
        cls.route = trekking_factories.RouteFactory.create()
        cls.practice = trekking_factories.PracticeFactory.create()
        cls.theme = common_factories.ThemeFactory.create()
        cls.trek = trekking_factories.TrekFactory.create(difficulty=cls.difficulty, published_fr=True, practice=cls.practice,
                                                         route=cls.route)
        cls.trek.accessibilities.add(cls.accessibility_1, cls.accessibility_2)
        cls.trek.networks.add(cls.trek_network)
        cls.trek.themes.add(cls.theme)
        cls.information_desk_type = tourism_factories.InformationDeskTypeFactory.create()
        cls.information_desk = tourism_factories.InformationDeskFactory.create(type=cls.information_desk_type)

    def get_settings(self, params=None):
        return self.client.get(reverse('apimobile:settings'), params, headers={"accept-language": 'fr'})

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

    def test_settings_information_desk_type(self):
        tourism_factories.InformationDeskTypeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        informationdesk_item = next((item.get('values') for item in json_response.get('data')
                                     if item['id'] == 'information_desk_types'), None)

        self.assertEqual(len(informationdesk_item), 1)
        self.assertEqual(informationdesk_item[0].get('name'), self.information_desk_type.label)
        self.assertIn(str(self.information_desk_type.pictogram), informationdesk_item[0].get('pictogram'))

    def test_settings_information_desk_type_no_picto(self):
        self.information_desk_type.pictogram = None
        self.information_desk_type.save()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        informationdesk_item = next((item.get('values') for item in json_response.get('data')
                                     if item['id'] == 'information_desk_types'), None)

        self.assertEqual(len(informationdesk_item), 1)
        self.assertEqual(informationdesk_item[0].get('name'), self.information_desk_type.label)
        self.assertIsNone(informationdesk_item[0].get('pictogram'))

    def test_settings_network(self):
        trekking_factories.TrekNetworkFactory(network="MDR")
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        network_item = next((item.get('values') for item in json_response.get('data')
                             if item['id'] == 'networks'), None)
        self.assertEqual(len(network_item), 1)
        self.assertEqual(network_item[0].get('name'), self.trek_network.network)
        self.assertIn(str(self.trek_network.pictogram), network_item[0].get('pictogram'))

    def test_settings_network_no_picto(self):
        # Should not happen directly, the picto is mandatory in the form, but could happen with an import
        self.trek_network.pictogram = None
        self.trek_network.save()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        network_item = next((item.get('values') for item in json_response.get('data')
                             if item['id'] == 'networks'), None)
        self.assertEqual(len(network_item), 1)
        self.assertEqual(network_item[0].get('name'), self.trek_network.network)
        self.assertIsNone(network_item[0].get('pictogram'))

    def test_settings_route(self):
        trekking_factories.RouteFactory()
        route_unpublished = trekking_factories.RouteFactory()
        self.trek_unpublished = trekking_factories.TrekFactory.create(route=route_unpublished, published=False)

        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        route_item = next((item.get('values') for item in json_response.get('data')
                           if item['id'] == 'route'), None)

        self.assertEqual(len(route_item), 1)
        self.assertEqual(route_item[0].get('name'), self.route.route)
        self.assertIn(str(self.route.pictogram), route_item[0].get('pictogram'))

    def test_settings_route_no_picto(self):
        self.route.pictogram = None
        self.route.save()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        route_item = next((item.get('values') for item in json_response.get('data')
                           if item['id'] == 'route'), None)

        self.assertEqual(len(route_item), 1)
        self.assertEqual(route_item[0].get('name'), self.route.route)
        self.assertIsNone(route_item[0].get('pictogram'))

    def test_settings_practice(self):
        trekking_factories.PracticeFactory()
        practice_unpublished = trekking_factories.PracticeFactory()
        self.trek_unpublished = trekking_factories.TrekFactory.create(practice=practice_unpublished, published=False)

        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        practice_item = next((item.get('values') for item in json_response.get('data')
                              if item['id'] == 'practice'), None)
        self.assertEqual(len(practice_item), 1)
        self.assertEqual(practice_item[0].get('name'), self.practice.name)
        self.assertIn(str(self.practice.pictogram), practice_item[0].get('pictogram'))

    def test_settings_accessibility_not_used(self):
        trekking_factories.AccessibilityFactory.create()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        accessibility_item = next((item.get('values') for item in json_response.get('data')
                                   if item['id'] == 'accessibilities'), None)
        self.assertEqual(len(accessibility_item), 2)
        self.assertEqual(accessibility_item[0].get('name'), self.accessibility_2.name)
        self.assertIn(str(self.accessibility_2.pictogram), accessibility_item[0].get('pictogram'))

    def test_settings_accessibility(self):
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        accessibility_item = next((item.get('values') for item in json_response.get('data')
                                   if item['id'] == 'accessibilities'), None)
        self.assertEqual(len(accessibility_item), 2)

    def test_settings_accessibility_no_picto(self):
        accessibility = trekking_factories.AccessibilityFactory.create(pictogram=None)
        self.trek.accessibilities.add(accessibility)
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        accessibility_item = next((item.get('values') for item in json_response.get('data')
                                   if item['id'] == 'accessibilities'), None)
        self.assertEqual(len(accessibility_item), 3)
        self.assertIn(accessibility.name, [a.get('name') for a in accessibility_item])
        self.assertIn(None, [a.get('pictogram') for a in accessibility_item])

    def test_settings_difficulty(self):
        trekking_factories.DifficultyLevelFactory()
        difficulty_unpublished = trekking_factories.DifficultyLevelFactory()
        self.trek_unpublished = trekking_factories.TrekFactory.create(difficulty=difficulty_unpublished, published=False)

        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        difficulty_item = next((item.get('values') for item in json_response.get('data')
                                if item['id'] == 'difficulty'), None)
        self.assertEqual(len(difficulty_item), 1)
        self.assertEqual(difficulty_item[0].get('name'), self.difficulty.difficulty)
        self.assertIn(str(self.difficulty.pictogram), difficulty_item[0].get('pictogram'))

    def test_settings_difficulty_no_picto(self):
        self.difficulty.pictogram = None
        self.difficulty.save()
        difficulty = trekking_factories.DifficultyLevelFactory(pictogram=None)
        trekking_factories.DifficultyLevelFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        difficulty_item = next((item.get('values') for item in json_response.get('data')
                                if item['id'] == 'difficulty'), None)
        self.assertEqual(len(difficulty_item), 1)
        self.assertEqual(difficulty_item[0].get('name'), difficulty.difficulty)
        self.assertIsNone(difficulty_item[0].get('pictogram'))

    def test_settings_theme(self):
        common_factories.ThemeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        theme_item = next((item.get('values') for item in json_response.get('data')
                           if item['id'] == 'themes'), None)
        self.assertEqual(len(theme_item), 1)
        self.assertEqual(theme_item[0].get('name'), self.theme.label)
        self.assertIn(str(self.theme.pictogram), theme_item[0].get('pictogram'))

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
        self.assertIn(city.name, [c.get('name') for c in city_item])
        self.assertIn(city.code, [c.get('id') for c in city_item])

    def test_settings_district(self):
        district = zoning_factories.DistrictFactory()
        zoning_factories.DistrictFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        district_item = next((item.get('values') for item in json_response.get('data')
                              if item['id'] == 'districts'), None)
        self.assertEqual(len(district_item), District.objects.count())
        self.assertIn(district.name, [d.get('name') for d in district_item])

    def test_settings_poi_type(self):
        poi_type = trekking_factories.POITypeFactory.create()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        poi_type_item = next((item.get('values') for item in json_response.get('data')
                              if item['id'] == 'poi_types'), None)
        self.assertEqual(len(poi_type_item), POIType.objects.count())
        self.assertEqual(poi_type_item[0].get('label'), poi_type.label)
        self.assertIn(str(poi_type.pictogram), poi_type_item[0].get('pictogram'))

    def test_settings_poi_type_no_picto(self):
        # Should not happen directly, the picto is mandatory in the form, but could happen with an import
        poi_type = trekking_factories.POITypeFactory.create(pictogram=None)
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        poi_type_item = next((item.get('values') for item in json_response.get('data')
                              if item['id'] == 'poi_types'), None)
        self.assertEqual(len(poi_type_item), POIType.objects.count())
        self.assertEqual(poi_type_item[0].get('label'), poi_type.label)
        self.assertIsNone(poi_type_item[0].get('pictogram'))

    def test_settings_touristic_content_type(self):
        type1 = tourism_factories.TouristicContentType1Factory()
        tourism_factories.TouristicContentType2Factory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        touristic_content_type_item = next((item.get('values') for item in json_response.get('data')
                                            if item['id'] == 'touristiccontent_types'), None)
        self.assertEqual(len(touristic_content_type_item), TouristicContentType.objects.count())
        self.assertEqual(touristic_content_type_item[0].get('name'), type1.label)
        self.assertIn(str(type1.pictogram), touristic_content_type_item[0].get('pictogram'))

    def test_settings_touristic_content_type_no_picto(self):
        type1 = tourism_factories.TouristicContentType1Factory(pictogram=None)
        tourism_factories.TouristicContentType2Factory(pictogram=None)
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        touristic_content_type_item = next((item.get('values') for item in json_response.get('data')
                                            if item['id'] == 'touristiccontent_types'), None)
        self.assertEqual(len(touristic_content_type_item), TouristicContentType.objects.count())
        self.assertEqual(touristic_content_type_item[0].get('name'), type1.label)
        self.assertIsNone(touristic_content_type_item[0].get('pictogram'))

    def test_settings_touristic_event_type(self):
        type_event = tourism_factories.TouristicEventTypeFactory()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        touristic_event_type_item = next((item.get('values') for item in json_response.get('data')
                                          if item['id'] == 'touristicevent_types'), None)
        self.assertEqual(len(touristic_event_type_item), TouristicEventType.objects.count())
        self.assertEqual(touristic_event_type_item[0].get('name'), type_event.type)
        self.assertIn(str(type_event.pictogram), touristic_event_type_item[0].get('pictogram'))

    def test_settings_touristic_event_type_no_picto(self):
        type_event = tourism_factories.TouristicEventTypeFactory(pictogram=None)
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        touristic_event_type_item = next((item.get('values') for item in json_response.get('data')
                                          if item['id'] == 'touristicevent_types'), None)
        self.assertEqual(len(touristic_event_type_item), TouristicEventType.objects.count())
        self.assertEqual(touristic_event_type_item[0].get('name'), type_event.type)
        self.assertIsNone(touristic_event_type_item[0].get('pictogram'))

    def test_settings_touristic_content_category(self):
        category = tourism_factories.TouristicContentCategoryFactory.create()
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        category_item = next((item.get('values') for item in json_response.get('data')
                              if item['id'] == 'touristiccontent_categories'), None)
        self.assertEqual(len(category_item), TouristicContentCategory.objects.count())
        self.assertEqual(category_item[0].get('name'), category.label)
        self.assertIn(str(category.pictogram), category_item[0].get('pictogram'))

    def test_settings_touristic_content_category_no_picto(self):
        category = tourism_factories.TouristicContentCategoryFactory.create(pictogram=None)
        response = self.get_settings()
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        category_item = next((item.get('values') for item in json_response.get('data')
                              if item['id'] == 'touristiccontent_categories'), None)
        self.assertEqual(len(category_item), TouristicContentCategory.objects.count())
        self.assertEqual(category_item[0].get('name'), category.label)
        self.assertIsNone(category_item[0].get('pictogram'))
