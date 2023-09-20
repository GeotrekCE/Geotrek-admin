from freezegun import freeze_time
from difflib import SequenceMatcher

from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings

from geotrek.sensitivity.tests.factories import SensitiveAreaFactory, SpeciesFactory
from geotrek.trekking.tests.factories import TrekFactory


def similar_string(a: str, b: str) -> float:
    """compare two strings and return similarity ratio

    Args:
        a (str): first value
        b (str): second_value

    Returns:
        float: Similarity ration
    """
    return SequenceMatcher(None, a, b).ratio()


class SensitiveAreaModelTest(TestCase):
    def test_specific_radius(self):
        specie = SpeciesFactory.create(radius=50)
        sensitive_area = SensitiveAreaFactory.create(species=specie)
        self.assertEqual(sensitive_area.radius, 50)

    def test_no_radius(self):
        sensitive_area = SensitiveAreaFactory.create()
        self.assertEqual(sensitive_area.radius, settings.SENSITIVITY_DEFAULT_RADIUS)

    def test_get_lang_published(self):
        sensitive_area = SensitiveAreaFactory.create()
        self.assertEqual(
            sensitive_area.published_langs, list(settings.MODELTRANSLATION_LANGUAGES)
        )

    def test_get_lang_not_published(self):
        sensitive_area = SensitiveAreaFactory.create()
        sensitive_area.published = False
        self.assertEqual(sensitive_area.published_langs, [])

    def test_get_extent(self):
        sensitive_area = SensitiveAreaFactory.create(
            geom="POLYGON((700000 6600000, 700000 6600100, 700100 6600100, 700100 6600000, 700000 6600000))"
        )
        lng_min, lat_min, lng_max, lat_max = sensitive_area.extent
        self.assertAlmostEqual(lng_min, 3)
        self.assertAlmostEqual(lat_min, 46.5)
        self.assertAlmostEqual(lng_max, 3.00130397)
        self.assertAlmostEqual(lat_max, 46.50090044)

    def test_get_kml(self):
        species = SpeciesFactory.create(radius=5)
        sensitive_area = SensitiveAreaFactory.create(species=species)
        self.assertIn(
            "<coordinates>3.0,46.5,5.0 3.0,46.500027,5.0 3.0000391,46.500027,5.0 "
            "3.0000391,46.5,5.0 3.0,46.5,5.0</coordinates>",
            sensitive_area.kml(),
        )

    def test_get_kml_point(self):
        sensitive_area = SensitiveAreaFactory.create(geom="POINT(700000 6600000)")
        # Create a buffer around the point with 100 (settings.SENSITIVITY_DEFAULT_RADIUS)
        self.assertIn(
            "<coordinates>"
            "3.001304,46.5,0.0 3.0012047,46.4996554,0.0 3.000922,46.4993633,0.0 "
            "3.000499,46.4991681,0.0 3.0,46.4990996,0.0 2.999501,46.4991681,0.0 "
            "2.999078,46.4993633,0.0 2.9987953,46.4996554,0.0 2.998696,46.5,0.0 "
            "2.9987953,46.5003446,0.0 2.999078,46.5006367,0.0 2.999501,46.5008319,0.0 "
            "3.0,46.5009004,0.0 3.000499,46.5008319,0.0 3.000922,46.5006367,0.0 "
            "3.0012047,46.5003446,0.0 3.001304,46.5,0.0"
            "</coordinates>",
            sensitive_area.kml(),
        )

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice1",
        ]
    )
    @freeze_time("2020-01-01")
    def test_get_openair_data(self):
        sensitive_area = SensitiveAreaFactory.create()
        self.assertEqual(
            "AC ZSM\n"
            "AN Species\n"
            f"*AUID GUId=! UId=! Id=(Identifiant-GeoTrek-sentivity) {sensitive_area.pk}\n"
            "*ADescr Species (published on 01/01/2020)\n"
            '*ATimes {"6": ["UTC(01/06->30/06)", "ANY(00:00->23:59)"],"7": ["UTC(01/07->31/07)", "ANY(00:00->23:59)"]}\n'
            "AH 329FT AGL\n"
            "DP 46:29:59 N 03:00:00 E\n"
            "DP 46:30:00 N 03:00:00 E",
            sensitive_area.openair(),
        )

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice1",
        ]
    )
    @freeze_time("2020-01-01")
    def test_get_openair_point_data(self):
        species = SpeciesFactory.create(radius=300)
        sensitive_area = SensitiveAreaFactory.create(geom="POINT(700000 6600000)", species=species)
        self.assertEqual(
            "AC ZSM\n"
            "AN Species\n"
            f"*AUID GUId=! UId=! Id=(Identifiant-GeoTrek-sentivity) {sensitive_area.pk}\n"
            "*ADescr Species (published on 01/01/2020)\n"
            '*ATimes {"6": ["UTC(01/06->30/06)", "ANY(00:00->23:59)"],"7": ["UTC(01/07->31/07)", "ANY(00:00->23:59)"]}\n'
            "AH 985FT AGL\n"
            "DP 46:29:59 N 03:00:14 E\n"
            "DP 46:29:50 N 03:00:00 E\n"
            "DP 46:29:59 N 02:59:45 E\n"
            "DP 46:30:09 N 03:00:00 E",
            sensitive_area.openair(),
        )

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice1",
        ]
    )
    def test_get_openair_data_with_radius(self):
        species = SpeciesFactory.create(radius=300)
        sensitive_area = SensitiveAreaFactory.create(species=species)
        self.assertIn("AH 985FT AGL", sensitive_area.openair())

    def test_is_public(self):
        sensitive_area = SensitiveAreaFactory.create()
        self.assertTrue(sensitive_area.is_public())
        sensitive_area.published = False
        self.assertFalse(sensitive_area.is_public())

    @override_settings(SENSITIVE_AREA_INTERSECTION_MARGIN=0)
    def test_trek_sensitive_area(self):
        """
        The area intersects 6 times the trek : we should get only one time this area.
        issue #2010
        """
        SensitiveAreaFactory.create()
        SensitiveAreaFactory.create(
            geom="Polygon ((700000 6600000, 699994.87812128441873938 6600014.35493460204452276, 700021.84601664706133306"
            " 6600008.61177170090377331, 700013.10642092768102884 6600028.83769322279840708, 700044.81866825232282281"
            " 6600017.85077288933098316, 700030.83531510119792074 6600042.32164090406149626, 700061.79845422133803368"
            " 6600043.07074910867959261, 700061.04934601683635265 6600069.78894173633307219, 700075.78180737234652042"
            " 6600056.55469678994268179, 700072.53567181946709752 6600088.01724137924611568, 700092.26218787173274904"
            " 6600081.27526753861457109, 700090.01486325822770596 6600097.75564803835004568, 700100 6600100, "
            "700100 6600000, 700000 6600000))"
        )
        trek = TrekFactory.create()
        self.assertEqual(trek.published_sensitive_areas.count(), 2)

    def test_geom_buffered_trigger(self):
        """Geom buffered could be created and updated in instance after creation"""
        area = SensitiveAreaFactory()
        self.assertIsNotNone(area.geom_buffered)
