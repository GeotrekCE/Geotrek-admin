from django.test import TestCase
from mapentity.tests import SuperUserFactory

from ...authent.models import default_structure
from ..forms import RegulatorySensitiveAreaForm
from .factories import RegulatorySensitiveAreaFactory, SportPracticeFactory


class RegulatorySensitiveAreaFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sensitive_area = RegulatorySensitiveAreaFactory()
        cls.sport_practice = SportPracticeFactory()
        cls.user = SuperUserFactory()
        cls.default_structure = default_structure()

    def test_form_valid_with_correct_data(self):
        form_data = {
            "name": "Test Area",
            "elevation": 100,
            "pictogram": None,
            "practices": [self.sport_practice.id],
            "url": "http://test.com",
            "period01": True,
            "period02": False,
            "period03": True,
            "period04": False,
            "period05": True,
            "period06": False,
            "period07": True,
            "period08": False,
            "period09": True,
            "period10": False,
            "period11": True,
            "period12": False,
            "instance": self.sensitive_area,
            "structure": self.default_structure.pk,
            "geom": "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
        }
        form = RegulatorySensitiveAreaForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_without_name(self):
        form_data = {
            "name": "",
            "elevation": 100,
            "pictogram": None,
            "practices": [self.sport_practice.id],
            "url": "http://test.com",
            "period01": True,
            "period02": False,
            "period03": True,
            "period04": False,
            "period05": True,
            "period06": False,
            "period07": True,
            "period08": False,
            "period09": True,
            "period10": False,
            "period11": True,
            "period12": False,
            "instance": self.sensitive_area,
            "structure": self.default_structure.pk,
            "geom": "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
        }
        form = RegulatorySensitiveAreaForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_form_save_new_instance(self):
        form_data = {
            "name": "Test Area",
            "elevation": 100,
            "pictogram": None,
            "practices": [self.sport_practice.id],
            "url": "http://test.com",
            "period01": True,
            "period02": False,
            "period03": True,
            "period04": False,
            "period05": True,
            "period06": False,
            "period07": True,
            "period08": False,
            "period09": True,
            "period10": False,
            "period11": True,
            "period12": False,
            "geom": "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
            "structure": self.default_structure.pk,
        }
        form = RegulatorySensitiveAreaForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        area = form.save()
        self.assertEqual(area.species.name, form_data["name"])
        self.assertEqual(area.species.radius, form_data["elevation"])
        self.assertEqual(area.species.url, form_data["url"])
        self.assertEqual(area.species.practices.count(), len(form_data["practices"]))
        for p in range(1, 13):
            fieldname = f"period{p:02}"
            self.assertEqual(getattr(area.species, fieldname), form_data[fieldname])

    def test_form_save_existing_instance(self):
        form_data = {
            "name": "Test Area",
            "elevation": 100,
            "pictogram": None,
            "practices": [self.sport_practice.id],
            "url": "http://test.com",
            "period01": True,
            "period02": False,
            "period03": True,
            "period04": False,
            "period05": True,
            "period06": False,
            "period07": True,
            "period08": False,
            "period09": True,
            "period10": False,
            "period11": True,
            "period12": False,
            "geom": "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
            "structure": self.default_structure.pk,
        }
        form = RegulatorySensitiveAreaForm(
            data=form_data, instance=self.sensitive_area, user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)
        area = form.save()
        self.assertEqual(area.species.name, form_data["name"])
        self.assertEqual(area.species.radius, form_data["elevation"])
        self.assertEqual(area.species.url, form_data["url"])
        self.assertEqual(area.species.practices.count(), len(form_data["practices"]))
        for p in range(1, 13):
            fieldname = f"period{p:02}"
            self.assertEqual(getattr(area.species, fieldname), form_data[fieldname])
