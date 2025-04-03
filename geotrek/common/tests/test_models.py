import os

from django.core.files import File
from django.test import TestCase

from geotrek.authent.models import default_structure
from geotrek.authent.tests.factories import (
    StructureFactory,
    UserFactory,
    UserProfileFactory,
)
from geotrek.common.models import Theme
from geotrek.common.tests.factories import (
    HDViewPointFactory,
    LabelFactory,
    OrganismFactory,
)
from geotrek.trekking.tests.factories import TrekFactory


class ThemeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data"
        )
        cls.files = [f for f in os.listdir(cls.directory)]

    def test_pictogram(self):
        self.path = os.path.join(self.directory, "picto.png")
        self.assertEqual(os.path.getsize(self.path), 6203)
        self.theme = Theme.objects.create()
        with open(self.path, "rb") as picto_file:
            self.theme.pictogram = File(picto_file)
            file = self.theme.pictogram_off
            path_off = os.path.join(self.directory, "picto_off.png")
            self.assertEqual(os.path.getsize(path_off), 3445)
            self.assertEqual(file.name, path_off)

    def tearDown(self):
        for f in os.listdir(self.directory):
            if f not in self.files:
                os.remove(os.path.join(self.directory, f))


class LabelTest(TestCase):
    def test_str(self):
        label = LabelFactory.create(name="foo")
        self.assertEqual(str(label), "foo")


class OrganismTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organism_with_structure = OrganismFactory.create(
            structure=default_structure()
        )
        cls.organism_without_structure = OrganismFactory.create()

    def test_str_with_structure(self):
        self.assertEqual(
            f"{self.organism_with_structure}",
            f"{self.organism_with_structure.organism} ({self.organism_with_structure.structure.name})",
        )

    def test_str_without_structure(self):
        self.assertEqual(
            f"{self.organism_without_structure}",
            self.organism_without_structure.organism,
        )


class HDViewPointTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        structure = StructureFactory(name="MyStructure")
        cls.trek = TrekFactory(structure=structure)
        cls.vp = HDViewPointFactory(content_object=cls.trek, title="Panorama")
        cls.user = UserFactory()
        UserProfileFactory(structure=structure, user=cls.user)

    def test_thumbnail_url(self):
        self.assertEqual(
            self.vp.thumbnail_url,
            f"/api/hdviewpoint/drf/hdviewpoints/{self.vp.pk}/data/thumbnail.png?source=vips",
        )

    def test_tiles_url(self):
        self.assertEqual(
            self.vp.get_generic_picture_tile_url(),
            f"/api/hdviewpoint/drf/hdviewpoints/{self.vp.pk}/tiles/{{z}}/{{x}}/{{y}}.png?source=vips",
        )

    def test_properties(self):
        self.assertEqual(str(self.vp), "Panorama")
        self.assertIn("admin/", self.vp.get_list_url())
