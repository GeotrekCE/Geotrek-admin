import datetime
import os
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
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
    AttachmentFactory,
    HDViewPointFactory,
    LabelFactory,
    OrganismFactory,
)
from geotrek.trekking.tests.factories import TrekFactory
from geotrek.zoning.tests.factories import CityFactory


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


class ProviderTestCase(TestCase):
    def test_str(self):
        provider = Provider.objects.create(name="foo")
        self.assertEqual(str(provider), "foo")

    def test_template_validator(self):
        template = (
            "<a href='http://test/object/{{object.eid|safe}}'>{{object.eid|safe}}</a>"
        )
        provider = Provider(name="foo", link_template=template)
        provider.full_clean()

        self.assertEqual(provider.link_template, template)


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


class GeotrekMapEntityMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.structure1 = StructureFactory(name="Structure 1")
        cls.structure2 = StructureFactory(name="Structure 2")
        cls.user = UserFactory()
        cls.profile = UserProfileFactory(user=cls.user, structure=cls.structure2)

    def test_duplicate_without_request(self):
        trek = TrekFactory.create(name="Original Trek", structure=self.structure1)
        clone = trek.duplicate()
        self.assertEqual(clone.name, "Original Trek (copy)")
        self.assertEqual(clone.structure, self.structure1)

    def test_duplicate_with_request_and_user_structure(self):
        trek = TrekFactory.create(name="Original Trek", structure=self.structure1)

        # Mock request
        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(self.user)
        clone = trek.duplicate(request=request)
        self.assertEqual(clone.name, "Original Trek (copy)")
        self.assertEqual(clone.structure, self.structure2)

    def test_duplicate_with_request_no_user(self):
        trek = TrekFactory.create(name="Original Trek", structure=self.structure1)

        class MockRequest:
            pass

        request = MockRequest()
        clone = trek.duplicate(request=request)
        self.assertEqual(clone.structure, self.structure1)

    def test_duplicate_with_request_user_no_profile(self):
        trek = TrekFactory.create(name="Original Trek", structure=self.structure1)

        class MockUser:
            pass

        user = MockUser()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(user)
        clone = trek.duplicate(request=request)
        self.assertEqual(clone.structure, self.structure1)

    def test_duplicate_with_request_user_profile_is_none(self):
        trek = TrekFactory.create(name="Original Trek", structure=self.structure1)

        class MockUser:
            profile = None

        user = MockUser()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(user)
        clone = trek.duplicate(request=request)
        self.assertEqual(clone.structure, self.structure1)

    def test_duplicate_with_request_user_profile_no_structure(self):
        trek = TrekFactory.create(name="Original Trek", structure=self.structure1)

        class MockProfile:
            pass

        class MockUser:
            profile = MockProfile()

        user = MockUser()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(user)
        clone = trek.duplicate(request=request)
        self.assertEqual(clone.structure, self.structure1)

    def test_duplicate_with_request_user_profile_structure_is_none(self):
        trek = TrekFactory.create(name="Original Trek", structure=self.structure1)

        class MockProfile:
            structure = None

        class MockUser:
            profile = MockProfile()

        user = MockUser()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(user)
        clone = trek.duplicate(request=request)
        self.assertEqual(clone.structure, self.structure1)


class CommonMixinsComprehensiveCoverageTest(TestCase):
    def test_timestamp_mixin(self):
        from geotrek.common.mixins.models import app_settings
        from geotrek.trekking.models import Trek

        trek = TrekFactory.create()
        self.assertIsNotNone(trek.date_insert_display)
        self.assertIsNotNone(trek.date_update_display)

        agg = Trek.last_update_and_count
        self.assertEqual(agg["count"], 1)

        lu = Trek.latest_updated()
        self.assertIsNotNone(lu)

        lu2, cnt2 = Trek.latest_updated_with_count()
        self.assertEqual(cnt2, 1)

        lu3, cnt3 = Trek.latest_updated_with_count(z=0, x=0, y=0)
        self.assertEqual(cnt3, 0)  # Doesn't intersect fake coordinates

        # Test FieldError exception branch
        with patch.dict(app_settings, {"DATE_UPDATE_FIELD_NAME": "invalid_field"}):
            lu_err, cnt_err = Trek.latest_updated_with_count()
            self.assertIsNone(lu_err)
            self.assertEqual(cnt_err, 0)

        # Test latest_updated DoesNotExist branch
        with patch.object(Trek.objects, "only", side_effect=Trek.DoesNotExist):
            self.assertIsNone(Trek.latest_updated())

    def test_nodelete_mixin(self):
        from geotrek.trekking.models import Trek

        trek = TrekFactory.create()
        trek.delete(force=False)
        self.assertTrue(trek.deleted)

        pk = trek.pk
        trek.delete(force=True)
        self.assertFalse(Trek.objects.filter(pk=pk).exists())

    def test_pictures_mixin(self):
        trek = TrekFactory.create()

        self.assertEqual(len(trek.pictures), 0)
        self.assertEqual(trek.serializable_pictures, [])
        self.assertEqual(trek.serializable_pictures_mobile(1), [])
        self.assertIsNone(trek.resized_picture_mobile(1))
        self.assertIsNone(trek.picture_print)
        self.assertEqual(trek.thumbnail_display, "None")

        # Test pre-fetched _pictures
        trek._pictures = ["fake_picture"]
        self.assertEqual(trek.pictures, ["fake_picture"])
        del trek._pictures

        # Create image attachment
        image_content = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        uploaded_image = SimpleUploadedFile(
            "test.gif", image_content, content_type="image/gif"
        )

        AttachmentFactory.create(
            content_object=trek,
            attachment_file=uploaded_image,
            is_image=True,
            author="Author Name",
            title="Image Title",
            legend="Image Legend",
            starred=True,
        )

        self.assertEqual(len(trek.pictures), 1)
        self.assertEqual(len(trek.sorted_attachments), 1)
        self.assertIsNotNone(trek.thumbnail_verbose_name)

        # Test resized_pictures with internal exception handling inside loop
        with patch("geotrek.common.mixins.models.get_thumbnailer") as mock_thumb:

            class MockThumbnailer:
                def get_options(self, options):
                    return {}

                def get_thumbnail(self, options):
                    msg = "Thumbnail error"
                    raise Exception(msg)

            mock_thumb.return_value = MockThumbnailer()
            self.assertEqual(trek.resized_pictures, [])

        # Test get_thumbnail exception logging
        with patch("geotrek.common.mixins.models.get_thumbnailer") as mock_thumb:

            class MockThumbnailer2:
                def get_thumbnail(self, options):
                    msg = "Mock error"
                    raise Exception(msg)

            mock_thumb.return_value = MockThumbnailer2()
            self.assertIsNone(trek.get_thumbnail("small-square"))

        # Test success path for pictures mixin with a valid mock thumbnailer
        mock_thumb_file = MagicMock()
        mock_thumb_file.name = "thumb.png"

        with patch("geotrek.common.mixins.models.get_thumbnailer") as mock_thumb:

            class MockThumbnailer3:
                def get_options(self, options):
                    return {}

                def get_thumbnail(self, options):
                    return mock_thumb_file

            mock_thumb.return_value = MockThumbnailer3()

            self.assertEqual(len(trek.resized_pictures), 1)
            self.assertEqual(len(trek.serializable_pictures), 1)
            self.assertEqual(len(trek.serializable_pictures_mobile(1)), 1)
            self.assertIsNotNone(trek.resized_picture_mobile(1))
            self.assertIsNotNone(trek.get_thumbnail("small-square"))
            self.assertIsNotNone(trek.picture_print)
            self.assertIsNotNone(trek.thumbnail)
            self.assertIn("thumb.png", trek.thumbnail_display)

    def test_publishable_mixin(self):
        # Test base properties
        trek = TrekFactory.create(name="Beautiful Trek", published=True)
        self.assertEqual(trek.name_csv_display, "Beautiful Trek")
        self.assertTrue(trek.is_public())
        self.assertEqual(trek.slug, "beautiful-trek")

        # Test review email sending
        with patch("geotrek.common.mixins.models.mail_managers") as mock_mail:
            with patch.object(settings, "ALERT_REVIEW", True):
                # Review changed to True on existing object
                trek.review = True
                trek.save()
                self.assertTrue(mock_mail.called)

            # If mail_managers fails, it logs warning
            mock_mail.side_effect = Exception("Mail error")
            with patch.object(settings, "ALERT_REVIEW", True):
                trek.review = False
                trek.save()
                trek.review = True
                trek.save()  # Should log warning but not raise exception

        # Test published_status and published_langs
        from modeltranslation.utils import build_localized_fieldname

        with patch.object(settings, "PUBLISHED_BY_LANG", True):
            # Populate at least one translation published field to True
            for language in settings.MAPENTITY_CONFIG["TRANSLATED_LANGUAGES"]:
                setattr(trek, build_localized_fieldname("published", language[0]), True)
                break

            status = trek.published_status
            self.assertIsNotNone(status)
            langs = trek.published_langs
            self.assertIsNotNone(langs)
            self.assertTrue(trek.any_published)

            # Test any_published and is_public returning False under translation modes
            trek.published = False
            for language in settings.MAPENTITY_CONFIG["TRANSLATED_LANGUAGES"]:
                setattr(
                    trek, build_localized_fieldname("published", language[0]), False
                )
            self.assertFalse(trek.any_published)
            self.assertFalse(trek.is_public())

        with patch.object(settings, "PUBLISHED_BY_LANG", False):
            trek.published = True
            self.assertTrue(trek.any_published)

            # Call the mixin's is_public directly to bypass subclass overriding
            from geotrek.common.mixins.models import BasePublishableMixin

            self.assertTrue(BasePublishableMixin.is_public(trek))

            # published_status under PUBLISHED_BY_LANG=False
            status_false = trek.published_status
            self.assertIsNotNone(status_false)

            # published_langs under self.published=True
            trek.published = True
            langs_true = trek.published_langs
            self.assertIsNotNone(langs_true)
            self.assertTrue(trek.is_public())

            # published_langs under self.published=False
            trek.published = False
            self.assertFalse(trek.any_published)
            langs_false = trek.published_langs
            self.assertEqual(langs_false, [])
            self.assertFalse(trek.is_public())

            # save() with publication_date logic
            trek.publication_date = datetime.date.today()
            trek.save()
            self.assertIsNone(trek.publication_date)

        # Test completeness fields
        completeness = {"trek": ["name"]}
        with patch.object(settings, "COMPLETENESS_FIELDS", completeness):
            self.assertTrue(trek.is_complete())
            self.assertTrue(trek.is_publishable())

        completeness = {"trek": ["description_teaser"]}
        with patch.object(settings, "COMPLETENESS_FIELDS", completeness):
            trek.description_teaser = ""
            self.assertFalse(trek.is_complete())
            self.assertFalse(trek.is_publishable())

        # Test name_display HTML formatting
        trek.published = True
        self.assertIn("badge-success", trek.name_display)
        trek.published = False
        trek.review = True
        self.assertIn("badge-warning", trek.name_display)

    def test_pictogram_mixin(self):
        theme = Theme.objects.create()
        self.assertEqual(theme.pictogram_img(), "No pictogram")
        self.assertIsNone(theme.get_pictogram_url())

        # Set a dummy pictogram
        theme.pictogram = SimpleUploadedFile(
            "icon.png", b"dummy", content_type="image/png"
        )
        theme.save()
        self.assertIn("icon.png", theme.get_pictogram_url())
        self.assertIn("pictogram_png", theme.pictogram_img())

    def test_add_property_mixin(self):
        from geotrek.common.mixins.models import AddPropertyMixin

        class TestClass(AddPropertyMixin):
            pass

        def dummy_func(self):
            return "dummy_val"

        TestClass.add_property("my_prop", dummy_func, "My Verbose Name")
        inst = TestClass()
        self.assertEqual(inst.my_prop, "dummy_val")
        self.assertEqual(inst.my_prop_verbose_name, "My Verbose Name")

        with self.assertRaises(AttributeError):
            TestClass.add_property("my_prop", dummy_func, "My Verbose Name")

    def test_prepare_map_image(self):
        from geotrek.trekking.models import Trek

        trek = TrekFactory.create()

        # Test without mapimage attachment (calls super().prepare_map_image)
        with patch("mapentity.models.MapEntityMixin.prepare_map_image") as mock_super:
            trek.prepare_map_image("http://localhost")
            self.assertTrue(mock_super.called)

        # Test with mapimage attachment by mocking the query to return a mock picture
        mock_picture = MagicMock()
        mock_picture.attachment_file.path = "fake_src.png"

        mock_manager = MagicMock()
        mock_manager.filter.return_value.first.return_value = mock_picture

        with patch.object(Trek, "attachments", new=mock_manager):
            with patch.object(trek, "get_map_image_path", return_value="fake_dst.png"):
                with patch("shutil.copyfile") as mock_copy:
                    trek.prepare_map_image("http://localhost")
                    self.assertTrue(mock_copy.called)

    def test_bbox_mixin(self):
        city = CityFactory.create()
        self.assertIsNotNone(city.bbox)
