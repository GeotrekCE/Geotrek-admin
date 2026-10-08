from django.forms.models import inlineformset_factory
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.authent.tests.factories import UserFactory
from geotrek.zoning.forms import MapFilterForm, VigilancePeriodForm
from geotrek.zoning.models import VigilanceArea, VigilancePeriod
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    VigilanceAreaFactory, VigilancePeriodFactory,
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


# class VigilancePeriodFormsetTest(TestCase):
#     def test_formset_initial_values_with_multiple_items(self):
#         """
#         Test that initial values for active_days and active_months (which use ArrayField)
#         are correctly loaded as lists and not as serialized strings when creating/editing
#         VigilanceArea through the form.
#         """
#
#         period = VigilancePeriodFactory(active_days=[1, 2], active_months=[3, 4])
#         form = VigilancePeriodFormset(user=UserFactory(), instance=period.vigilance_area)
#         print(form.__dict__)
#         self.assertEqual(form.initial["active_days"], [1, 2])
#         self.assertEqual(form.initial["active_months"], [3, 4])
#
#     def test_form_validation_and_save_with_multiple_items(self):
#         """
#         Test that the form validates and correctly saves multiple active_days and
#         active_months values.
#         """
#         area = VigilanceAreaFactory()
#         data = {
#             "name_en": "Area test",
#             "structure": area.structure.pk,
#             "vigilance_area_type": area.vigilance_area_type.pk,
#             "practicability": area.practicability,
#             "vigilance_level": area.vigilance_level.pk,
#             "start_date": area.start_date,
#             "geom": "SRID=4326;MULTIPOLYGON(((-0.3142392 -1.0870745, -0.4442674 1.9698002, 2.6553568 2.0446445, 2.6683833 -1.0177449, -0.3142392 -1.0870745)))",
#             "active_days": [1, 2],
#             "active_months": [3, 4],
#         }
#         form = VigilanceAreaForm(user=UserFactory(), instance=area, data=data)
#         self.assertTrue(form.is_valid(), form.errors)
#         saved_area = form.save()
#         self.assertEqual(saved_area.active_days, [1, 2])
#         self.assertEqual(saved_area.active_months, [3, 4])


class VigilancePeriodFormSetTest(TestCase):
    PREFIX = "periods"

    @classmethod
    def setUpTestData(cls):
        cls.area = VigilanceAreaFactory.create(periods=[])
        cls.formset = inlineformset_factory(
            VigilanceArea, VigilancePeriod, form=VigilancePeriodForm
        )

    def build_formset(self, data, instance=None):
        return self.formset(data, instance=instance or self.area)

    def management_data(self, total, initial=0):
        return {
            f"{self.PREFIX}-TOTAL_FORMS": str(total),
            f"{self.PREFIX}-INITIAL_FORMS": str(initial),
            f"{self.PREFIX}-MIN_NUM_FORMS": "0",
            f"{self.PREFIX}-MAX_NUM_FORMS": "1000",
        }

    def test_multiple_active_days_and_months(self):
        data = {
            **self.management_data(1),
            f"{self.PREFIX}-0-start_date": "2026-01-01",
            f"{self.PREFIX}-0-end_date": "2026-12-31",
            f"{self.PREFIX}-0-active_days": [1, 3, 5],
            f"{self.PREFIX}-0-active_months": [6, 7, 8],
            f"{self.PREFIX}-0-annual": "on",
        }
        formset = self.build_formset(data)
        self.assertTrue(formset.is_valid(), formset.errors)

        formset.save()
        period = self.area.periods.first()
        self.assertEqual(list(period.active_days), [1, 3, 5])
        self.assertEqual(list(period.active_months), [6, 7, 8])

    def test_empty_days_and_months_are_valid(self):
        data = {
            **self.management_data(1),
            f"{self.PREFIX}-0-start_date": "2026-01-01",
            f"{self.PREFIX}-0-end_date": "2026-03-31",
        }
        formset = self.build_formset(data)
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        period = self.area.periods.first()
        self.assertEqual(period.active_days, [])
        self.assertEqual(period.active_months, [])

    def test_multiple_periods_for_same_area(self):
        data = {
            **self.management_data(3),
            f"{self.PREFIX}-0-start_date": "2026-01-01",
            f"{self.PREFIX}-0-end_date": "2026-02-28",
            f"{self.PREFIX}-0-active_days": [1, 2],
            f"{self.PREFIX}-1-start_date": "2026-05-01",
            f"{self.PREFIX}-1-end_date": "2026-06-30",
            f"{self.PREFIX}-1-active_months": [5, 6],
            f"{self.PREFIX}-2-start_date": "2026-09-01",
            f"{self.PREFIX}-2-end_date": "2026-10-31",
            f"{self.PREFIX}-2-active_days": [6],
            f"{self.PREFIX}-2-active_months": [9, 10],
            f"{self.PREFIX}-2-annual": True,
        }
        formset = self.build_formset(data)
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()

        periods = self.area.periods.order_by("start_date")
        self.assertEqual(periods.count(), 3)
        self.assertEqual(periods[0].active_days, [1, 2])
        self.assertEqual(periods[1].active_months, [5, 6])
        self.assertEqual(periods[2].active_days, [6])
        self.assertEqual(periods[2].active_months, [9, 10])
        self.assertTrue(periods[2].annual)

    def test_edit_and_delete_existing_periods(self):
        p1 = VigilancePeriodFactory.create(
            vigilance_area=self.area,
            start_date="2026-01-01",
            end_date="2026-02-01",
            active_days=[1],
        )
        p2 = VigilancePeriodFactory.create(
            vigilance_area=self.area,
            start_date="2026-03-01",
            end_date="2026-04-01",
        )
        data = {
            **self.management_data(2, initial=2),
            f"{self.PREFIX}-0-id": str(p1.pk),
            f"{self.PREFIX}-0-start_date": "2026-01-01",
            f"{self.PREFIX}-0-end_date": "2026-02-01",
            f"{self.PREFIX}-0-active_days": [1, 2, 3],
            f"{self.PREFIX}-1-id": str(p2.pk),
            f"{self.PREFIX}-1-start_date": "2026-03-01",
            f"{self.PREFIX}-1-end_date": "2026-04-01",
            f"{self.PREFIX}-1-DELETE": "on",
        }
        formset = self.build_formset(data)
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()

        self.assertEqual(self.area.periods.count(), 1)
        p1.refresh_from_db()
        self.assertEqual(list(p1.active_days), [1, 2, 3])


