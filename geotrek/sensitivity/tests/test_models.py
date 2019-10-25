# -*- coding: utf-8 -*-
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
        self.assertIn('<coordinates>3.0,46.5,5.0 3.0,46.5000270135,5.0 3.00003911867,46.5000270135,5.0 3.00003911866,'
                      '46.5,5.0 3.0,46.5,5.0</coordinates>', sensitive_area.kml())

    def test_get_kml_point(self):
        sensitive_area = SensitiveAreaFactory.create(geom='POINT(700000 6600000)')
        # Create a buffer around the point with 100 (settings.SENSITIVITY_DEFAULT_RADIUS)
        self.assertIn('<coordinates>3.00130395519,46.4999999926,0.0 3.0012046899,46.4996554064,0.0 3.00092202479,'
                      '46.4993632821,0.0 3.00049899443,46.4991680917,0.0 3.0,46.4990995501,0.0 2.99950100557,'
                      '46.4991680917,0.0 2.99907797521,46.4993632821,0.0 2.9987953101,46.4996554064,0.0 2.99869604481,'
                      '46.4999999926,0.0 2.99879529488,46.5003445809,0.0 2.99907795368,46.5006367104,0.0 2.99950099034,'
                      '46.500831906,0.0 3.0,46.5009004498,0.0 3.00049900966,46.500831906,0.0 3.00092204632,'
                      '46.5006367104,0.0 3.00120470512,46.5003445809,0.0 3.00130395519,46.4999999926,0.0</coordinates>',
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
