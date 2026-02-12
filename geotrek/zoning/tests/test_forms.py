from django.test import TestCase
from django.test.utils import override_settings

from geotrek.zoning.forms import MapFilterForm
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
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
