from django.contrib.admin import AdminSite
from django.test import TestCase
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory

from geotrek.zoning.admin import VigilanceAreaTypeAdmin, VigilanceLevelAdmin
from geotrek.zoning.models import (
    City,
    District,
    RestrictedArea,
    VigilanceAreaType,
    VigilanceLevel,
)
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    VigilanceLevelFactory,
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

    def test_color_markup(self):
        vigilance_level = VigilanceLevelFactory(color="#AC2F89")
        admin = VigilanceLevelAdmin(VigilanceLevel, AdminSite())
        self.assertEqual(
            admin.color_markup(vigilance_level),
            '<span style="color: #AC2F89;">⬤</span> #AC2F89',
        )

    def test_no_color_markup(self):
        vigilance_level = VigilanceLevelFactory(color="")
        admin = VigilanceLevelAdmin(VigilanceLevel, AdminSite())
        self.assertEqual(admin.color_markup(vigilance_level), "")

    def test_vigilance_level_form(self):
        admin = VigilanceLevelAdmin(VigilanceLevel, AdminSite())
        form = admin.get_form(None)
        self.assertEqual(
            form.base_fields["level"].help_text,
            "Level 1 is considered the highest vigilance level.",
        )

    def test_vigilance_area_types_form(self):
        admin = VigilanceAreaTypeAdmin(VigilanceAreaType, AdminSite())
        form = admin.get_form(None)

        self.assertEqual(
            form.base_fields["code"].help_text,
            "If left empty, the code of the nearest parent that has one is used.",
        )
        self.assertEqual(
            form.base_fields["pictogram"].help_text,
            "If left empty, the pictogram of the nearest parent that has one is used.",
        )
