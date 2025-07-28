from django.conf import settings
from django.contrib.gis.geos import MultiPoint, MultiPolygon, Point, Polygon
from django.test.testcases import TestCase
from django.urls import reverse

from geotrek.sensitivity.models import SensitiveArea
from geotrek.sensitivity.tests import factories as sensitivity_factory
from geotrek.tourism.tests import factories as tourism_factory
from geotrek.trekking import models as trek_models
from geotrek.trekking.tests import factories as trek_factory
from geotrek.zoning.tests import factories as zoning_factory

GEOJSON_STRUCTURE = sorted(["features", "type"])

DETAIL_GEOJSON_STRUCTURE = sorted(["geometry", "type", "properties", "id"])

DETAIL_TREK_GEOJSON_STRUCTURE = sorted(["geometry", "bbox", "type", "properties", "id"])

TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE = sorted(
    [
        "id",
        "name",
        "slug",
        "accessibilities",
        "description_teaser",
        "cities",
        "districts",
        "description",
        "departure",
        "arrival",
        "access",
        "advised_parking",
        "advice",
        "difficulty",
        "length",
        "ascent",
        "descent",
        "route",
        "duration",
        "labels",
        "min_elevation",
        "max_elevation",
        "themes",
        "networks",
        "practice",
        "pictures",
        "information_desks",
        "departure_city",
        "arrival_city",
        "parking_location",
        "profile",
        "points_reference",
        "ambiance",
        "children",
    ]
)


TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(
    [
        "id",
        "first_picture",
        "name",
        "departure",
        "accessibilities",
        "duration",
        "districts",
        "difficulty",
        "practice",
        "themes",
        "length",
        "cities",
        "route",
        "departure_city",
        "ascent",
        "descent",
    ]
)

POI_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(
    ["id", "description", "name", "pictures", "type"]
)

TOURISTIC_EVENT_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(
    [
        "id",
        "name",
        "description_teaser",
        "description",
        "themes",
        "pictures",
        "begin_date",
        "end_date",
        "duration",
        "start_time",
        "contact",
        "email",
        "website",
        "organizer",
        "organizers",
        "speaker",
        "type",
        "accessibility",
        "meeting_point",
        "capacity",
        "booking",
        "target_audience",
        "practical_info",
        "approved",
    ]
)

TOURISTIC_CONTENT_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(
    [
        "id",
        "description",
        "description_teaser",
        "category",
        "themes",
        "contact",
        "email",
        "website",
        "practical_info",
        "pictures",
        "type1",
        "type2",
        "approved",
        "reservation_id",
        "reservation_system",
        "name",
    ]
)

SENSITIVE_AREA_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(
    ["id", "description", "name", "practices", "contact", "info_url", "period"]
)


class BaseApiTest(TestCase):
    """
    Base TestCase for all API profile
    """

    @classmethod
    def setUpTestData(cls):
        cls.nb_treks = 1

        cls.treks = trek_factory.TrekWithPublishedPOIsFactory.create_batch(
            cls.nb_treks,
            name_fr="Coucou",
            description_fr="Sisi",
            description_teaser_fr="mini",
            published_fr=True,
            points_reference=MultiPoint(
                [Point(0, 0), Point(1, 1)], srid=settings.API_SRID
            ),
            parking_location=Point(0, 0, srid=settings.API_SRID),
        )
        cls.trek = cls.treks[0]
        cls.trek_parent = trek_factory.TrekFactory(
            name_fr="Parent",
            description_fr="Parent_1",
            description_teaser_fr="Parent_1",
            published_fr=True,
        )
        cls.trek_child_published = trek_factory.TrekFactory(
            name_fr="Child_published",
            description_fr="Child_published_1",
            description_teaser_fr="Child_published_1",
            published_fr=True,
        )
        cls.trek_child_not_published = trek_factory.TrekFactory(
            name_fr="Child_not_published",
            description_fr="Child_not_published_1",
            description_teaser_fr="Child_not_published_1",
            published_fr=False,
            published_en=True,
            published=False,
        )
        trek_models.OrderedTrekChild(
            parent=cls.trek_parent, child=cls.trek_child_published, order=1
        ).save()
        trek_models.OrderedTrekChild(
            parent=cls.trek_parent, child=cls.trek_child_not_published, order=0
        ).save()

        cls.trek_parent_not_published = trek_factory.TrekFactory(
            name_fr="Parent_not_published",
            description_fr="Parent_not_published_1",
            description_teaser_fr="Parent_not_published_1",
            published_fr=False,
            published_en=True,
            published=False,
        )
        cls.trek_child_published_2 = trek_factory.TrekFactory(
            name_fr="Child_published_2",
            description_fr="Child_published_2",
            description_teaser_fr="Child_published_2",
            published_fr=True,
        )
        cls.trek_child_not_published_2 = trek_factory.TrekFactory(
            name_fr="Child_not_published_2",
            description_fr="Child_not_published_2",
            description_teaser_fr="Child_not_published_2",
            published_fr=False,
            published_en=True,
            published=False,
        )
        trek_models.OrderedTrekChild(
            parent=cls.trek_parent_not_published,
            child=cls.trek_child_published_2,
            order=2,
        ).save()
        trek_models.OrderedTrekChild(
            parent=cls.trek_parent_not_published,
            child=cls.trek_child_not_published_2,
            order=1,
        ).save()

        cls.touristic_content = tourism_factory.TouristicContentFactory(
            geom=cls.trek.published_pois.first().geom,
            name_fr="Coucou_Content",
            description_fr="Sisi",
            description_teaser_fr="mini",
            published_fr=True,
        )

        cls.touristic_event = tourism_factory.TouristicEventFactory(
            geom=cls.trek.published_pois.first().geom,
            name_fr="Coucou_Event",
            description_fr="Sisi_Event",
            description_teaser_fr="mini",
            published_fr=True,
        )

        trek_geom_envelope = cls.trek.geom.envelope
        cls.sensitive_area_species = sensitivity_factory.SensitiveAreaFactory(
            geom=trek_geom_envelope, published=True
        )
        cls.sensitive_area_regulatory = sensitivity_factory.SensitiveAreaFactory(
            geom=trek_geom_envelope, published=True
        )

        cls.district = zoning_factory.DistrictFactory(
            geom=MultiPolygon(Polygon.from_bbox(cls.trek.geom.extent))
        )
        cls.district2 = zoning_factory.DistrictFactory(
            geom=MultiPolygon(Polygon.from_bbox(cls.trek.geom.extent)), published=False
        )
        bigger_extent = (
            cls.trek.geom.extent[0] - 1,
            cls.trek.geom.extent[1] - 1,
            cls.trek.geom.extent[2] + 1,
            cls.trek.geom.extent[3] + 1,
        )
        cls.city = zoning_factory.CityFactory(
            geom=MultiPolygon(Polygon.from_bbox(bigger_extent))
        )
        cls.city2 = zoning_factory.CityFactory(
            geom=MultiPolygon(Polygon.from_bbox(bigger_extent)), published=False
        )

    def get_treks_list(self, lang, params=None):
        return self.client.get(
            reverse("apimobile:treks-list"), params, headers={"accept-language": lang}
        )

    def get_treks_detail(self, id_trek, lang, params=None):
        return self.client.get(
            reverse("apimobile:treks-detail", args=(id_trek,)),
            params,
            headers={"accept-language": lang},
        )

    def get_poi_list(self, id_trek, lang, params=None):
        return self.client.get(
            reverse("apimobile:treks-pois", args=(id_trek,)),
            params,
            headers={"accept-language": lang},
        )

    def get_touristic_content_list(self, id_trek, lang, params=None):
        return self.client.get(
            reverse("apimobile:treks-touristic-contents", args=(id_trek,)),
            params,
            headers={"accept-language": lang},
        )

    def get_touristic_event_list(self, id_trek, lang, params=None):
        return self.client.get(
            reverse("apimobile:treks-touristic-events", args=(id_trek,)),
            params,
            headers={"accept-language": lang},
        )

    def get_sensitive_area_list(self, id_trek, lang, params=None):
        return self.client.get(
            reverse("apimobile:treks-sensitive-areas", args=(id_trek,)),
            params,
            headers={"accept-language": lang},
        )


class APIAccessTestCase(BaseApiTest):
    """
    TestCase for administrator API profile
    """

    @classmethod
    def setUpTestData(cls):
        #  created user
        BaseApiTest.setUpTestData()

    def test_trek_detail(self):
        response = self.get_treks_detail(self.trek.pk, "fr")
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()), DETAIL_TREK_GEOJSON_STRUCTURE)
        self.assertEqual(
            sorted(json_response.get("properties").keys()),
            TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE,
        )

        self.assertEqual("Coucou", json_response.get("properties").get("name"))
        self.assertEqual("Sisi", json_response.get("properties").get("description"))
        self.assertEqual(
            "mini", json_response.get("properties").get("description_teaser")
        )
        self.assertAlmostEqual(
            0, json_response.get("properties").get("points_reference")[0][0]
        )
        self.assertAlmostEqual(
            0, json_response.get("properties").get("parking_location")[0]
        )
        self.assertEqual(len(json_response["properties"]["districts"]), 1)
        self.assertListEqual(json_response["properties"]["cities"], [self.city.id])
        self.assertEqual(json_response["properties"]["departure_city"], self.city.id)
        self.assertEqual(
            json_response["properties"]["arrival_city"], self.city.id, json_response
        )

    def test_trek_detail_no_parking_location(self):
        trek_no_parking = trek_factory.TrekFactory(
            name_fr="no_parking", parking_location=None, published_fr=True
        )
        response = self.get_treks_detail(trek_no_parking.pk, "fr")
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()), DETAIL_TREK_GEOJSON_STRUCTURE)
        self.assertEqual(
            sorted(json_response.get("properties").keys()),
            TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE,
        )
        self.assertIsNone(json_response.get("properties").get("parking_location"))

    def test_trek_parent_detail(self):
        response = self.get_treks_detail(self.trek_parent.pk, "fr")
        self.assertEqual(response.status_code, 200)
        json_response_1 = response.json()
        self.assertEqual(sorted(json_response_1.keys()), DETAIL_TREK_GEOJSON_STRUCTURE)
        self.assertEqual(
            sorted(json_response_1.get("properties").keys()),
            TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE,
        )
        self.assertEqual("Parent", json_response_1.get("properties").get("name"))
        # Order is verified at the same time : not published then published
        self.assertEqual(
            [self.trek_child_not_published.pk, self.trek_child_published.pk],
            [
                child.get("properties").get("id")
                for child in json_response_1.get("properties")
                .get("children")
                .get("features")
            ],
        )
        response = self.get_treks_detail(self.trek_parent_not_published.pk, "fr")
        self.assertEqual(response.status_code, 404)

    def test_trek_children_detail_parent_published(self):
        # Not published => we got the detail because the parent is published
        response = self.get_treks_detail(self.trek_child_not_published.pk, "fr")
        self.assertEqual(response.status_code, 200)
        json_response_1 = response.json()
        self.assertEqual(sorted(json_response_1.keys()), DETAIL_TREK_GEOJSON_STRUCTURE)
        self.assertEqual(
            sorted(json_response_1.get("properties").keys()),
            TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE,
        )
        self.assertEqual(
            "Child_not_published", json_response_1.get("properties").get("name")
        )

        # Published
        response = self.get_treks_detail(self.trek_child_published.pk, "fr")
        self.assertEqual(response.status_code, 200)
        json_response_2 = response.json()
        self.assertEqual(sorted(json_response_2.keys()), DETAIL_TREK_GEOJSON_STRUCTURE)
        self.assertEqual(
            sorted(json_response_2.get("properties").keys()),
            TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE,
        )
        self.assertEqual(
            "Child_published", json_response_2.get("properties").get("name")
        )

    def test_trek_children_detail_parent_not_published(self):
        # Not published => we don't got the detail because the parent is not published
        response = self.get_treks_detail(self.trek_child_not_published_2.pk, "fr")
        self.assertEqual(response.status_code, 404)

        response = self.get_treks_detail(self.trek_child_not_published_2.pk, "en")
        self.assertEqual(response.status_code, 200)

        # Published anyway even if if there is a parent behind not published
        response = self.get_treks_detail(self.trek_child_published_2.pk, "fr")
        self.assertEqual(response.status_code, 200)
        json_response_2 = response.json()
        self.assertEqual(sorted(json_response_2.keys()), DETAIL_TREK_GEOJSON_STRUCTURE)
        self.assertEqual(
            sorted(json_response_2.get("properties").keys()),
            TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE,
        )
        self.assertEqual(
            "Child_published_2", json_response_2.get("properties").get("name")
        )

    def test_trek_list(self):
        response = self.get_treks_list("fr")
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()

        # trek count is ok (1 normal trek 1 parent published linked with 1 children published (2)
        # and 1 children published with 1 parent not published => 4
        self.assertEqual(len(json_response.get("features")), 4)
        features = json_response.get("features")
        ids = [features[i].get("properties").get("id") for i in range(len(features))]
        pks_expected = [
            self.trek.pk,
            self.trek_parent.pk,
            self.trek_child_published_2.pk,
            self.trek_child_published.pk,
        ]
        self.assertCountEqual(ids, pks_expected)
        # test dim 2 ok
        self.assertEqual(
            len(json_response.get("features")[0].get("geometry").get("coordinates")), 2
        )

        self.assertEqual(
            sorted(json_response.get("features")[0].keys()), DETAIL_GEOJSON_STRUCTURE
        )

        self.assertEqual(
            sorted(json_response.get("features")[0].get("properties").keys()),
            TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE,
        )

        self.assertEqual(
            "Coucou", json_response.get("features")[0].get("properties").get("name")
        )
        self.assertIsNone(
            json_response.get("features")[0].get("properties").get("description")
        )
        self.assertIsNone(
            json_response.get("features")[0].get("properties").get("description_teaser")
        )
        self.assertEqual(
            json_response.get("features")[0].get("properties").get("departure_city"),
            self.city.id,
        )
        self.assertListEqual(
            json_response.get("features")[0].get("properties").get("cities"),
            [self.city.id],
        )

    def test_poi_list(self):
        response = self.get_poi_list(self.trek.pk, "fr")
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()), GEOJSON_STRUCTURE)

        # poi count by trek is ok
        self.assertEqual(
            len(json_response.get("features")), self.trek.published_pois.count()
        )

        # test dim 2 ok
        self.assertEqual(
            sorted(json_response.get("features")[0].keys()), DETAIL_GEOJSON_STRUCTURE
        )
        self.assertEqual(
            len(json_response.get("features")[0].get("geometry").get("coordinates")), 2
        )

        self.assertEqual(
            sorted(json_response.get("features")[0].get("properties").keys()),
            POI_LIST_PROPERTIES_GEOJSON_STRUCTURE,
        )

    def test_touristic_event_list(self):
        response = self.get_touristic_event_list(self.trek.pk, "fr")
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()), GEOJSON_STRUCTURE)

        # touristic events count by trek is ok
        self.assertEqual(
            len(json_response.get("features")),
            self.trek.published_touristic_events.count(),
        )

        # test dim 2 ok
        self.assertEqual(
            sorted(json_response.get("features")[0].keys()), DETAIL_GEOJSON_STRUCTURE
        )
        self.assertEqual(
            len(json_response.get("features")[0].get("geometry").get("coordinates")), 2
        )

        self.assertEqual(
            sorted(json_response.get("features")[0].get("properties").keys()),
            TOURISTIC_EVENT_LIST_PROPERTIES_GEOJSON_STRUCTURE,
        )
        self.assertEqual(
            json_response.get("features")[0].get("properties")["description"],
            "Sisi_Event",
        )

    def test_touristic_content_list(self):
        response = self.get_touristic_content_list(self.trek.pk, "fr")
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()), GEOJSON_STRUCTURE)

        # touristic contents count by trek is ok
        self.assertEqual(
            len(json_response.get("features")),
            self.trek.published_touristic_contents.count(),
        )

        # test dim 2 ok
        self.assertEqual(
            sorted(json_response.get("features")[0].keys()), DETAIL_GEOJSON_STRUCTURE
        )
        self.assertEqual(
            len(json_response.get("features")[0].get("geometry").get("coordinates")), 2
        )

        self.assertEqual(
            sorted(json_response.get("features")[0].get("properties").keys()),
            TOURISTIC_CONTENT_LIST_PROPERTIES_GEOJSON_STRUCTURE,
        )
        self.assertEqual(
            json_response.get("features")[0].get("properties")["description"], "Sisi"
        )

    def test_sensitive_area_list(self):
        response = self.get_sensitive_area_list(self.trek.pk, "fr")
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()), GEOJSON_STRUCTURE)

        # sensitive areas count by trek is ok
        self.assertEqual(
            len(json_response.get("features")),
            self.trek.published_sensitive_areas.count(),
        )

        for feature in json_response.get("features"):
            # test dim 2 ok
            self.assertEqual(sorted(feature.keys()), DETAIL_GEOJSON_STRUCTURE)
            self.assertEqual(len(feature.get("geometry").get("coordinates")[0][0]), 2)
            self.assertEqual(
                sorted(feature.get("properties").keys()),
                SENSITIVE_AREA_LIST_PROPERTIES_GEOJSON_STRUCTURE,
            )
            sensitive_area_obj = SensitiveArea.objects.get(pk=feature.get("id"))
            for i, month in enumerate([f"period{p:02}" for p in range(1, 13)]):
                self.assertEqual(
                    getattr(sensitive_area_obj.species, month),
                    feature.get("properties").get("period")[i],
                )


class APISwaggerTestCase(BaseApiTest):
    """
    TestCase for administrator API profile
    """

    @classmethod
    def setUpTestData(cls):
        BaseApiTest.setUpTestData()

    def test_schema_status_code(self):
        response = self.client.get(reverse("apimobile:schema"))
        self.assertEqual(response.status_code, 200)
