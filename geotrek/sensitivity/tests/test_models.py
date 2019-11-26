from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings

from geotrek.sensitivity.factories import SensitiveAreaFactory, SpeciesFactory
from geotrek.trekking.factories import TrekFactory


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
        self.assertEqual(sensitive_area.published_langs, list(settings.MODELTRANSLATION_LANGUAGES))

    def test_get_lang_not_published(self):
        sensitive_area = SensitiveAreaFactory.create()
        sensitive_area.published = False
        self.assertEqual(sensitive_area.published_langs, [])

    def test_get_extent(self):
        sensitive_area = SensitiveAreaFactory.create(
            geom='POLYGON((700000 6600000, 700000 6600100, 700100 6600100, 700100 6600000, 700000 6600000))')
        lng_min, lat_min, lng_max, lat_max = sensitive_area.extent
        self.assertAlmostEqual(lng_min, 3.0)
        self.assertAlmostEqual(lat_min, 46.49999999256511)
        self.assertAlmostEqual(lng_max, 3.0013039767202154)
        self.assertAlmostEqual(lat_max, 46.500900449784226)

    def test_get_kml(self):
        species = SpeciesFactory.create(radius=5)
        sensitive_area = SensitiveAreaFactory.create(species=species)
        self.assertIn('<coordinates>2.9999999999999996,46.499999999999936,5.0 2.9999999999999996,'
                      '46.50002701349546,5.0 3.000039118674988,46.500027013488776,5.0 3.0000391186556086,'
                      '46.49999999999323,5.0 2.9999999999999996,46.499999999999936,5.0</coordinates>',
                      sensitive_area.kml())

    def test_get_kml_point(self):
        sensitive_area = SensitiveAreaFactory.create(geom='POINT(700000 6600000)')
        # Create a buffer around the point with 100 (settings.SENSITIVITY_DEFAULT_RADIUS)
        self.assertIn('<coordinates>3.001303955186855,46.499999992565094,'
                      '0.0 3.001204689895445,'
                      '46.499655406403406,0.0 3.000922024788654,'
                      '46.49936328205089,0.0 3.000498994433644,'
                      '46.499168091663066,0.0 2.9999999999999996,'
                      '46.499099550078014,0.0 2.999501005566355,'
                      '46.499168091663066,0.0 2.9990779752113452,'
                      '46.49936328205089,0.0 2.998795310104554,'
                      '46.499655406403406,0.0 2.998696044813144,'
                      '46.499999992565094,0.0 2.998795294878421,'
                      '46.50034458088425,0.0 2.9990779536783414,'
                      '46.50063671044532,0.0 2.9995009903402217,'
                      '46.5008319060417,0.0 2.9999999999999996,'
                      '46.50090044978422,0.0 3.0004990096597774,'
                      '46.5008319060417,0.0 3.0009220463216577,'
                      '46.50063671044532,0.0 3.001204705121578,'
                      '46.50034458088425,0.0 3.001303955186855,'
                      '46.499999992565094,0.0</coordinates>',
                      sensitive_area.kml())

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
                 "700100 6600000, 700000 6600000))")
        trek = TrekFactory.create()
        self.assertEqual(trek.published_sensitive_areas.count(), 2)
