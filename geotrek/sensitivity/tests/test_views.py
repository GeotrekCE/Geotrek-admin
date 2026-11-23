import datetime
import json

import mercantile
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import GEOSGeometry, Point
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from freezegun import freeze_time
from mapentity.tests import SuperUserFactory

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import StructureFactory, UserProfileFactory
from geotrek.sensitivity.tests.factories import (
    RegulatorySensitiveAreaFactory,
    SensitiveAreaFactory,
    SpeciesFactory,
)


class SensitiveAreaViewsSameStructureTests(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        profile = UserProfileFactory.create(
            user__username="homer", user__password="dooh"
        )
        cls.user = profile.user
        cls.user.user_permissions.add(
            Permission.objects.get(codename="add_sensitivearea")
        )
        cls.user.user_permissions.add(
            Permission.objects.get(codename="change_sensitivearea")
        )
        cls.user.user_permissions.add(
            Permission.objects.get(codename="delete_sensitivearea")
        )
        cls.user.user_permissions.add(
            Permission.objects.get(codename="read_sensitivearea")
        )
        cls.user.user_permissions.add(
            Permission.objects.get(codename="export_sensitivearea")
        )

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
        self.assertRedirects(
            response,
            reverse("sensitivity:sensitivearea_detail", kwargs={"pk": self.area2.pk}),
        )

    def test_can_delete_same_structure(self):
        url = reverse("sensitivity:sensitivearea_delete", kwargs={"pk": self.area1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = reverse("sensitivity:sensitivearea_delete", kwargs={"pk": self.area2.pk})
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse("sensitivity:sensitivearea_detail", kwargs={"pk": self.area2.pk}),
        )


class SensitiveAreaTemplatesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.area = SensitiveAreaFactory.create()
        cls.user = SuperUserFactory()

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_species_name_shown_in_detail_page(self):
        url = reverse("sensitivity:sensitivearea_detail", kwargs={"pk": self.area.pk})
        response = self.client.get(url)
        self.assertContains(response, self.area.species.name)

    def test_geojson_detail_buffers_point_by_species_radius(self):
        species = SpeciesFactory.create(radius=400)
        point_area = SensitiveAreaFactory.create(
            geom=Point(700000, 6600000, srid=settings.SRID), species=species
        )
        url = point_area.get_geojson_detail_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["geometry"]["type"], "Polygon")
        self.assertEqual(data["properties"]["radius"], 400)
        geom = GEOSGeometry(json.dumps(data["geometry"]), srid=settings.API_SRID)
        geom.transform(settings.SRID)
        self.assertAlmostEqual(geom.area, 3.14159265 * 400**2, delta=15000)

    def test_mvt_endpoint_serves_buffered_point_circle(self):
        species = SpeciesFactory.create(radius=300)
        point_area = SensitiveAreaFactory.create(
            geom=Point(700000, 6600000, srid=settings.SRID), species=species
        )
        point_wgs84 = point_area.geom.transform(4326, clone=True)
        tile_coords = mercantile.tile(point_wgs84.x, point_wgs84.y, 12)
        url = reverse(
            "sensitivity:sensitivearea-drf-mvt",
            kwargs={"z": tile_coords.z, "x": tile_coords.x, "y": tile_coords.y},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 0)

    def test_create_view_includes_radii_and_default_radius(self):
        species = SpeciesFactory.create(radius=250)
        url = reverse("sensitivity:sensitivearea_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        radii = json.loads(response.context["radii"])
        self.assertEqual(radii[str(species.pk)], 250)
        self.assertEqual(
            response.context["default_radius"], settings.SENSITIVITY_DEFAULT_RADIUS
        )


class SensitiveAreaOpenAirViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.area1 = SensitiveAreaFactory.create()
        cls.area2 = RegulatorySensitiveAreaFactory.create()
        cls.area3 = SensitiveAreaFactory.create(geom="POINT(700000 6600000)")
        species = SpeciesFactory(radius=100)
        cls.area4 = SensitiveAreaFactory.create(
            geom="POINT(700000 6600000)", species=species
        )

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice1",
        ]
    )
    @freeze_time("2020-01-01")
    def test_openair_detail(self):
        url = reverse(
            "sensitivity:sensitivearea_openair_detail", args=("en", self.area4.pk)
        )
        response = self.client.get(url, headers={"host": "testserver"})
        self.assertEqual(response.status_code, 200)
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        expected_response = b"* This file has been produced from GeoTrek sensitivity (https://geotrek.fr/) module from website http://testserver\n"
        "* Using pyopenair library (https://github.com/lpoaura/pyopenair)\n"
        "* This file was created on:  2020-01-01 00:00:00\n"
        "\n"
        "AC ZSM\n"
        "AN Species\n"
        f"*AUID GUId=! UId=! Id=(Identifiant-GeoTrek-sentivity) {self.area4.pk}\n"
        f"*ADescr Species (published on {today})\n"
        '*ATimes {"6": ["UTC(01/06->30/06)", "ANY(00:00->23:59)"],"7": ["UTC(01/07->31/07)", "ANY(00:00->23:59)"]}\n'
        "AH 329FT AGL\n"
        "AL SFC\n"
        "DP 46:29:59 N 03:00:04 E\n"
        "DP 46:29:56 N 03:00:00 E\n"
        "DP 46:29:59 N 02:59:55 E\n"
        "DP 46:30:03 N 03:00:00 E"
        self.assertContains(response, expected_response)

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice3",
        ]
    )
    @freeze_time("2020-01-01")
    def test_not_an_aerial_sensitiveaera_detail(self):
        url = reverse(
            "sensitivity:sensitivearea_openair_detail", args=("en", self.area1.pk)
        )
        response = self.client.get(url, headers={"host": "testserver"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"This is not an aerial area")

    @override_settings(
        SENSITIVITY_OPENAIR_SPORT_PRACTICES=[
            "Practice1",
        ]
    )
    @freeze_time("2020-01-01")
    def test_openair_list(self):
        url = reverse("sensitivity:sensitivearea_openair_list", args=("en",))
        response = self.client.get(url, headers={"host": "testserver"})
        self.assertEqual(response.status_code, 200)
        expected_response = "* This file has been produced from GeoTrek sensitivity (https://geotrek.fr/) "
        "module from website http://testserver\n"
        "* Using pyopenair library (https://github.com/lpoaura/pyopenair)\n"
        "* This file was created on:  2020-01-01 00:00:00\n"
        "\n"
        "AC ZSM\n"
        self.assertContains(response, expected_response)
