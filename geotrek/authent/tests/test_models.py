from django.test import TestCase, override_settings

from geotrek.authent.models import default_structure_pk
from geotrek.authent.tests.factories import StructureFactory


class StructureModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.structure = StructureFactory(name="Mércäntour")

    def test_str(self):
        self.structure = StructureFactory(name="Mércäntour")
        self.assertEqual(str(self.structure), "Mércäntour")

    @override_settings(TEST=False, DEFAULT_STRUCTURE_NAME="Mércäntour")
    def test_default_structure_pk_cache(self):
        """ Test if default structure pk is in cache to avoid unnecessary queries """
        with self.assertNumQueries(1):
            # request and set in cache
            default_structure_pk()

        with self.assertNumQueries(0):
            # get from cache
            default_structure_pk()
            default_structure_pk()
            default_structure_pk()
