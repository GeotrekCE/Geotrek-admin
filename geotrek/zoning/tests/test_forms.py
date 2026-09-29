from django.test import TestCase
from django.test.utils import override_settings

from geotrek.authent.tests.factories import UserFactory
from geotrek.zoning.forms import MapFilterForm, VigilanceAreaForm
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    VigilanceAreaFactory,
)


class MapFilterFormTest(TestCase):
    def test_form_fields_exist_with_settings_enabled(self):
        """
        Test that bbox_city and bbox_district fields are present when
        settings are enabled and objects exist.
        """
        CityFactory()
        DistrictFactory()
        RestrictedAreaFactory()

        with override_settings(
            LAND_BBOX_CITIES_ENABLED=True,
            LAND_BBOX_DISTRICTS_ENABLED=True,
            LAND_BBOX_AREAS_ENABLED=True,
        ):
            form = MapFilterForm()
            self.assertIn("bbox_city", form.fields)
            self.assertIn("bbox_district", form.fields)
            self.assertIn("bbox_restrictedarea", form.fields)

    def test_form_fields_not_exist_with_settings_disabled(self):
        """
        Test that bbox_city and bbox_district fields are NOT present when
        settings are disabled, even if objects exist.
        """
        CityFactory()
        DistrictFactory()
        RestrictedAreaFactory()

        with override_settings(
            LAND_BBOX_CITIES_ENABLED=False,
            LAND_BBOX_DISTRICTS_ENABLED=False,
            LAND_BBOX_AREAS_ENABLED=False,
        ):
            form = MapFilterForm()
            self.assertNotIn("bbox_city", form.fields)
            self.assertNotIn("bbox_district", form.fields)
            self.assertNotIn("bbox_restrictedarea", form.fields)

    def test_form_fields_not_exist_without_objects(self):
        """
        Tests that certain form fields are not included when no corresponding objects
        exist.
        """

        with override_settings(
            LAND_BBOX_CITIES_ENABLED=True,
            LAND_BBOX_DISTRICTS_ENABLED=True,
            LAND_BBOX_AREAS_ENABLED=True,
        ):
            form = MapFilterForm()
            self.assertNotIn("bbox_city", form.fields)
            self.assertNotIn("bbox_district", form.fields)
            self.assertNotIn("bbox_restrictedarea", form.fields)

    def test_form_validity(self):
        """
        Test form validation.
        """
        city = CityFactory()
        district = DistrictFactory()
        restricted = RestrictedAreaFactory()

        with override_settings(
            LAND_BBOX_CITIES_ENABLED=True,
            LAND_BBOX_DISTRICTS_ENABLED=True,
            LAND_BBOX_AREAS_ENABLED=True,
        ):
            data = {
                "bbox_city": city.pk,
                "bbox_district": district.pk,
                "bbox_restrictedarea": restricted.pk,
            }
            form = MapFilterForm(data=data)
            self.assertTrue(form.is_valid())


class VigilanceAreaFormTest(TestCase):
    def test_form_initial_values_with_multiple_items(self):
        """
        Test that initial values for active_days and active_months (which use ArrayField)
        are correctly loaded as lists and not as serialized strings when creating/editing
        VigilanceArea through the form.
        """
        area = VigilanceAreaFactory(active_days=[1, 2], active_months=[3, 4])
        form = VigilanceAreaForm(user=UserFactory(), instance=area)
        self.assertEqual(form.initial["active_days"], [1, 2])
        self.assertEqual(form.initial["active_months"], [3, 4])

    def test_form_validation_and_save_with_multiple_items(self):
        """
        Test that the form validates and correctly saves multiple active_days and
        active_months values.
        """
        area = VigilanceAreaFactory()
        data = {
            "name_en": "Area test",
            "structure": area.structure.pk,
            "vigilance_area_type": area.vigilance_area_type.pk,
            "practicability": area.practicability,
            "start_date": area.start_date,
            "geom": "SRID=4326;MULTIPOLYGON(((-0.3142392 -1.0870745, -0.4442674 1.9698002, 2.6553568 2.0446445, 2.6683833 -1.0177449, -0.3142392 -1.0870745)))",
            "active_days": [1, 2],
            "active_months": [3, 4],
        }
        form = VigilanceAreaForm(user=UserFactory(), instance=area, data=data)
        self.assertTrue(form.is_valid(), form.errors)
        saved_area = form.save()
        self.assertEqual(saved_area.active_days, [1, 2])
        self.assertEqual(saved_area.active_months, [3, 4])
