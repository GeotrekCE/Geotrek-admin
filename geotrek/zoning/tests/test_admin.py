from django.test import TestCase
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory

from geotrek.zoning.models import City, District, RestrictedArea
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
)


class ZoningAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_publish_city(self):
        CityFactory.create(published=True)
        CityFactory.create(published=False)
        data = {
            "action": "publish",
            "_selected_action": City.objects.all().values_list("pk", flat=True),
        }
        self.client.post(reverse("admin:zoning_city_changelist"), data, follow=True)
        self.assertEqual(City.objects.filter(published=False).count(), 0)

    def test_unpublish_city(self):
        CityFactory.create(published=True)
        CityFactory.create(published=False)
        data = {
            "action": "unpublish",
            "_selected_action": City.objects.all().values_list("pk", flat=True),
        }
        self.client.post(reverse("admin:zoning_city_changelist"), data, follow=True)
        self.assertEqual(City.objects.filter(published=False).count(), 2)

    def test_publish_district(self):
        DistrictFactory.create(published=True)
        DistrictFactory.create(published=False)
        data = {
            "action": "publish",
            "_selected_action": District.objects.all().values_list("pk", flat=True),
        }
        self.client.post(reverse("admin:zoning_district_changelist"), data, follow=True)
        self.assertEqual(City.objects.filter(published=False).count(), 0)

    def test_unpublish_district(self):
        DistrictFactory.create(published=True)
        DistrictFactory.create(published=False)
        data = {
            "action": "unpublish",
            "_selected_action": District.objects.all().values_list("pk", flat=True),
        }
        self.client.post(reverse("admin:zoning_district_changelist"), data, follow=True)
        self.assertEqual(District.objects.filter(published=False).count(), 2)

    def test_publish_area(self):
        RestrictedAreaFactory.create(published=True)
        RestrictedAreaFactory.create(published=False)
        data = {
            "action": "publish",
            "_selected_action": RestrictedArea.objects.all().values_list(
                "pk", flat=True
            ),
        }
        self.client.post(
            reverse("admin:zoning_restrictedarea_changelist"), data, follow=True
        )
        self.assertEqual(RestrictedArea.objects.filter(published=False).count(), 0)

    def test_unpublish_area(self):
        RestrictedAreaFactory.create(published=True)
        RestrictedAreaFactory.create(published=False)
        data = {
            "action": "unpublish",
            "_selected_action": RestrictedArea.objects.all().values_list(
                "pk", flat=True
            ),
        }
        self.client.post(
            reverse("admin:zoning_restrictedarea_changelist"), data, follow=True
        )
        self.assertEqual(RestrictedArea.objects.filter(published=False).count(), 2)
