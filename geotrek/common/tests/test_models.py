import os

from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase

from geotrek.authent.models import default_structure
from geotrek.authent.tests.factories import (
    StructureFactory,
    UserFactory,
    UserProfileFactory,
)
from geotrek.common.mixins.models import ExternalSourceMixin
from geotrek.common.models import Provider, Theme
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


class ProviderTest(TestCase):
    def test_str(self):
        provider = Provider.objects.create(name="foo")
        self.assertEqual(str(provider), "foo")

    def test_template_validator(self):
        template = (
            "<a href='http://test/object/{{object.eid|safe}}'>{{object.eid|safe}}</a>"
        )
        provider = Provider(name="foo", link_template=template)

        try:
            provider.full_clean()
        except ValidationError as e:
            self.fail(f"Validation should not fail for a correct template: {e}")

        self.assertEqual(provider.link_template, template)

    def test_template_validator_template_error(self):
        template = (
            "<a href='http://test/object/{% object.eid|safe %}'>{{object.eid|safe}}</a>"
        )
        provider = Provider(name="foo", link_template=template)

        with self.assertRaisesMessage(ValidationError, "Incorrect syntax: "):
            provider.full_clean()


class ExternalSourceMixinTest(TestCase):
    class Source(ExternalSourceMixin):
        pass

    @classmethod
    def setUpTestData(cls):
        cls.provider = Provider.objects.create(name="foo")

    def test_create(self):
        source = self.Source.objects.create(provider=self.provider, eid="67854224689")
        self.assertEqual(source.provider.name, "foo")
        self.assertEqual(source.eid, "67854224689")

    def test_get_eid_with_template_link(self):
        provider_with_template = Provider.objects.create(
            name="link",
            link_template="<a href='http://test/object/{{object.eid|safe}}'>{{object.eid|safe}}</a>",
        )
        source = self.Source.objects.create(
            eid="12345", provider=provider_with_template
        )
        self.assertEqual(source.get_eid, "<a href='http://test/object/12345'>12345</a>")

    def test_get_eid_without_template_link(self):
        source = self.Source.objects.create(eid="12345", provider=self.provider)
        self.assertEqual(source.get_eid, "12345")

    def test_get_eid_without_eid(self):
        source = self.Source.objects.create(provider=self.provider)
        self.assertEqual(source.get_eid, " <span class='none'>None</span>")

    def test_get_eid_without_provider(self):
        source = self.Source.objects.create(provider=self.provider)
        self.assertEqual(source.get_eid, " <span class='none'>None</span>")
