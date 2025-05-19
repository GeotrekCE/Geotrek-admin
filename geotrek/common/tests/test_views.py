import os
import shutil
import tempfile
from copy import deepcopy
from io import StringIO
from unittest import mock, skipIf

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from mapentity.tests import SuperUserFactory
from mapentity.tests.factories import UserFactory
from mapentity.views.generic import MapEntityList

import geotrek.trekking.parsers  # noqa  # noqa
from geotrek.common.forms import HDViewPointAnnotationForm
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.models import FileType, HDViewPoint
from geotrek.common.parsers import Parser
from geotrek.common.tasks import import_datas
from geotrek.common.tests.factories import (
    HDViewPointFactory,
    LicenseFactory,
    TargetPortalFactory,
)
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.core.models import Path
from geotrek.trekking.models import Trek
from geotrek.trekking.tests.factories import TrekFactory


class DocumentPublicPortalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portal_1 = TargetPortalFactory.create()
        cls.portal_2 = TargetPortalFactory.create()
        cls.trek = TrekFactory.create()
        cls.trek.portal.add(cls.portal_1)

    def init_temp_directory(self):
        settings_template = deepcopy(settings.TEMPLATES)

        dirs = list(settings_template[1]["DIRS"])
        self.temp_directory = tempfile.mkdtemp()
        shutil.copytree(
            os.path.join(
                "geotrek", "common", "tests", "data", "templates_portal", "trekking"
            ),
            os.path.join(self.temp_directory, "trekking"),
        )
        shutil.move(
            os.path.join(self.temp_directory, "trekking", "portal"),
            os.path.join(self.temp_directory, "trekking", f"portal_{self.portal_1.pk}"),
        )
        dirs[0] = self.temp_directory
        new_dir_template = tuple(dirs)
        settings_template[1]["DIRS"] = new_dir_template
        return settings_template

    @mock.patch("mapentity.helpers.requests.get")
    def test_trek_document_portal(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.content = b"xxx"

        with override_settings(TEMPLATES=self.init_temp_directory()):
            response = self.client.get(
                reverse(
                    "trekking:trek_printable",
                    kwargs={
                        "lang": "fr",
                        "pk": self.trek.pk,
                        "slug": self.trek.slug,
                    },
                ),
                {"portal": self.portal_1.pk},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            template_name=f"trekking/portal_{self.portal_1.pk}/trek_public_pdf.css",
        )
        self.assertTemplateUsed(
            response,
            template_name=f"trekking/portal_{self.portal_1.pk}/trek_public_pdf.html",
        )
        self.assertTemplateUsed(response, template_name="trekking/trek_public_pdf.html")
        self.assertTemplateUsed(
            response, template_name="trekking/trek_public_pdf_base.html"
        )

    @mock.patch("mapentity.helpers.requests.get")
    def test_trek_document_booklet_portal(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.content = b"xxx"

        with override_settings(TEMPLATES=self.init_temp_directory()):
            response = self.client.get(
                reverse(
                    "trekking:trek_booklet_printable",
                    kwargs={
                        "lang": "fr",
                        "pk": self.trek.pk,
                        "slug": self.trek.slug,
                    },
                ),
                {"portal": self.portal_1.pk},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            template_name=f"trekking/portal_{self.portal_1.pk}/trek_public_booklet_pdf.html",
        )
        self.assertTemplateUsed(
            response, template_name="trekking/trek_public_booklet_pdf.html"
        )
        self.assertTemplateUsed(
            response, template_name="trekking/trek_public_pdf_base.html"
        )

    @mock.patch("mapentity.helpers.requests.get")
    def test_trek_document_wrong_portal(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.content = b"xxx"

        with override_settings(TEMPLATES=self.init_temp_directory()):
            response = self.client.get(
                reverse(
                    "trekking:trek_printable",
                    kwargs={
                        "lang": "fr",
                        "pk": self.trek.pk,
                        "slug": self.trek.slug,
                    },
                ),
                {"portal": self.portal_2.pk},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(
            response,
            template_name=f"trekking/portal_{self.portal_1.pk}/trek_public_pdf.css",
        )
        self.assertTemplateNotUsed(
            response,
            template_name=f"trekking/portal_{self.portal_1.pk}/trek_public_pdf.html",
        )
        self.assertTemplateUsed(response, template_name="trekking/trek_public_pdf.html")
        self.assertTemplateUsed(
            response, template_name="trekking/trek_public_pdf_base.html"
        )


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.super_user = SuperUserFactory()

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_settings_json(self):
        url = reverse("common:settings_json")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_check_extents(self):
        """Admin can access to extents view"""
        url = reverse("common:check_extents")
        self.client.force_login(self.super_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_simple_user_check_extents(self):
        """Simple user can't access to extents view"""
        url = reverse("common:check_extents")
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    @override_settings(COLUMNS_LISTS={})
    @mock.patch("geotrek.common.mixins.views.logger")
    def test_custom_columns_mixin_error_log(self, mock_logger):
        # Create view where columns fields are omitted
        class MissingColumns(CustomColumnsMixin, MapEntityList):
            model = Path

        MissingColumns()
        # Assert logger raises error message
        message = "Cannot build columns for class MissingColumns.\nPlease define on this class either : \n  - a field 'columns'\nOR \n  - two fields 'mandatory_columns' AND 'default_extra_columns'"
        mock_logger.error.assert_called_with(message)


class ViewsImportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.super_user = SuperUserFactory()

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_import_form_access(self):
        self.client.force_login(user=self.user)
        url = reverse("common:import_dataset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cities")

    def test_import_form_access_other_language(self):
        self.client.force_login(user=self.user)
        url = reverse("common:import_dataset")
        response = self.client.get(url, headers={"accept-language": "fr"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Communes")

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Topology is enabled")
    def test_import_update_access(self):
        self.client.force_login(user=self.user)
        url = reverse("common:import_update_json")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_from_file_good_zip_file(self):
        self.client.force_login(user=self.super_user)

        with open("geotrek/common/tests/data/test.zip", "rb") as real_archive:
            url = reverse("common:import_dataset")
            choices = {
                choice: id_choice
                for id_choice, choice in self.client.get(url)
                .context["form"]
                .fields["parser"]
                .choices
            }
            response_real = self.client.post(
                url,
                {
                    "upload-file": "Upload",
                    "with-file-parser": choices["Cities"],
                    "with-file-file": real_archive,
                    "with-file-encoding": "UTF-8",
                },
            )
            self.assertEqual(response_real.status_code, 200)
            self.assertNotContains(response_real, "File must be of ZIP type.")

    @mock.patch("geotrek.common.tasks.current_task")
    @mock.patch("geotrek.common.tasks.import_datas.delay")
    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_import_from_file_good_geojson_file(
        self, mocked_stdout, mocked, mocked_current_task
    ):
        self.client.force_login(user=self.super_user)
        FileType.objects.create(type="Photographie")
        mocked.side_effect = import_datas
        mocked_current_task.request.id = "1"
        with open("geotrek/common/tests/data/test.geojson", "rb") as geojson:
            url = reverse("common:import_dataset")
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("id_with-file-file", resp.content.decode("utf-8"))
            choices = {
                choice: id_choice
                for id_choice, choice in self.client.get(url)
                .context["form"]
                .fields["parser"]
                .choices
            }
            response_real = self.client.post(
                url,
                {
                    "upload-file": "Upload",
                    "with-file-parser": choices["Import trek"],
                    "with-file-file": geojson,
                    "with-file-encoding": "UTF-8",
                },
            )
            self.assertEqual(response_real.status_code, 200)
        self.assertEqual(Trek.objects.count(), 1)

    @mock.patch("geotrek.common.tasks.import_datas.delay")
    def test_import_from_file_bad_file(self, mocked):
        self.client.force_login(user=self.super_user)

        Parser.label = "Test"

        fake_archive = SimpleUploadedFile(
            "file.doc", b"file_content", content_type="application/msword"
        )
        url = reverse("common:import_dataset")
        choices = {
            choice: id_choice
            for id_choice, choice in self.client.get(url)
            .context["form"]
            .fields["parser"]
            .choices
        }
        response_fake = self.client.post(
            url,
            {
                "upload-file": "Upload",
                "with-file-parser": choices["Cities"],
                "with-file-file": fake_archive,
                "with-file-encoding": "UTF-8",
            },
        )
        self.assertEqual(response_fake.status_code, 200)
        self.assertEqual(mocked.call_count, 1)

        Parser.label = None

    def test_import_form_no_parser_no_superuser(self):
        self.client.force_login(user=self.user)

        real_archive = open("geotrek/common/tests/data/test.zip", "rb+")
        url = reverse("common:import_dataset")

        response_real = self.client.post(
            url,
            {
                "upload-file": "Upload",
                "with-file-parser": "1",
                "with-file-file": real_archive,
                "with-file-encoding": "UTF-8",
            },
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertNotContains(response_real, '<form  method="post"')

    def test_import_from_web_bad_parser(self):
        self.client.force_login(user=self.super_user)

        url = reverse("common:import_dataset")

        response_real = self.client.post(
            url,
            {
                "import-web": "Upload",
                "without-file-parser": "99",
            },
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertContains(
            response_real,
            "Select a valid choice. 99 is not one of the available choices.",
        )
        # There is no parser available for user not superuser

    def test_import_from_web_good_parser(self):
        self.client.force_login(user=self.super_user)

        url = reverse("common:import_dataset")
        real_key = (
            self.client.get(url)
            .context["form_without_file"]
            .fields["parser"]
            .choices[0][0]
        )
        response_real = self.client.post(
            url,
            {
                "import-web": "Upload",
                "without-file-parser": real_key,
            },
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertNotContains(
            response_real,
            f"Select a valid choice. {real_key} is not one of the available choices.",
        )


class HDViewPointViewTest(TestCase):
    def setUp(self):
        ContentType.objects.clear_cache()

    @classmethod
    def setUpTestData(cls):
        # Create objects
        cls.trek = TrekFactory(published=False)
        cls.license = LicenseFactory()
        # Create user with proper permissions
        cls.user_perm = UserFactory.create()
        add_perm = Permission.objects.get(codename="add_hdviewpoint")
        read_perm = Permission.objects.get(codename="read_hdviewpoint")
        update_perm = Permission.objects.get(codename="change_hdviewpoint")
        delete_perm = Permission.objects.get(codename="delete_hdviewpoint")
        cls.user_perm.user_permissions.add(
            add_perm, read_perm, update_perm, delete_perm
        )
        # Prepare access to test image
        cls.directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data"
        )
        cls.files = [f for f in os.listdir(cls.directory)]

    def test_crud_view(self):
        """
        Test CRUD rights and views for HD View Point object
        """
        self.client.force_login(user=self.user_perm)
        # Test create view
        response = self.client.get(
            f"{HDViewPoint.get_add_url()}?object_id={self.trek.pk}&content_type={ContentType.objects.get_for_model(Trek).pk}"
        )
        self.assertEqual(response.status_code, 200)
        img = get_dummy_uploaded_image()
        data = {
            "picture": img,
            "title_en": "Un titre",
            "author": "Someone",
            "legend_en": "Something",
            "geom": "SRID=2154;POINT(0 0)",
            "license": self.license.pk,
        }
        response = self.client.post(
            f"{HDViewPoint.get_add_url()}?object_id={self.trek.pk}&content_type={ContentType.objects.get_for_model(Trek).pk}",
            data,
        )
        vp = HDViewPoint.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.trek, vp.content_object)
        self.assertIn("dummy_img", vp.picture.name)
        self.assertEqual(vp.title, "Un titre")
        self.assertEqual(vp.author, "Someone")
        self.assertEqual(vp.legend, "Something")
        self.assertEqual(vp.license, self.license)
        self.assertEqual(vp.geom, Point((0, 0), srid=2154))
        # TODO assert annotations

        # Test Update view
        response = self.client.get(vp.get_update_url())
        self.assertEqual(response.status_code, 200)
        img = get_dummy_uploaded_image()
        data = {
            "picture": img,
            "title_en": "Un titre",
            "author_en": "Someone",
            "legend_en": "Something else",
            "geom": "SRID=2154;POINT(0 0)",
        }
        response = self.client.post(vp.get_update_url(), data)
        self.assertRedirects(
            response,
            f"/hdviewpoint/{vp.pk}/",
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        vp = HDViewPoint.objects.first()
        self.assertEqual(vp.legend, "Something else")
        self.assertEqual(vp.license, None)

        # Test detail view
        response = self.client.get(vp.get_detail_url())
        self.assertIn(b"Un titre", response.content)

        # Test delete view
        vp = HDViewPoint.objects.first()
        response = self.client.post(vp.get_delete_url(), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(HDViewPoint.objects.count(), 0)

    def test_tiles_view(self):
        """
        Test access rights for HD View Point tile endpoint
        """
        # Create HD View point with a dummy image
        self.path = os.path.join(self.directory, "empty_image.jpg")
        self.assertEqual(os.path.getsize(self.path), 18438)
        viewpoint = HDViewPointFactory.create(
            object_id=self.trek.pk, content_type=ContentType.objects.get_for_model(Trek)
        )
        with open(self.path, "rb") as picto_file:
            viewpoint.picture = File(picto_file, name="empty_image.jpg")
            viewpoint.save()

        # Test unlogged user cannot access HD View Point tiles
        tile_url = viewpoint.get_picture_tile_url(x=0, y=0, z=0)
        response = self.client.get(tile_url)
        self.assertEqual(response.status_code, 403)

        # Test unlogged user can access HD View Point tiles if related trek is published
        self.trek.published = True
        self.trek.save()
        response = self.client.get(tile_url)
        self.assertEqual(response.status_code, 200)
        self.trek.published = False  # Revert to previous state
        self.trek.save()

        # Test logged in user can access HD View Point tiles
        self.client.force_login(user=self.user_perm)
        response = self.client.get(tile_url)
        self.assertEqual(response.status_code, 200)

    def test_annotate_view(self):
        """
        Test annotations form view contains form and title
        """
        self.client.force_login(user=self.user_perm)
        vp = HDViewPointFactory(content_object=self.trek)
        response = self.client.get(vp.get_annotate_url())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], HDViewPointAnnotationForm)

    def test_viewset(self):
        self.client.force_login(user=self.user_perm)
        vp = HDViewPointFactory(content_object=self.trek)
        response = self.client.get(
            reverse(
                "common:hdviewpoint-drf-detail",
                kwargs={"pk": vp.pk, "format": "geojson"},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json().get("properties"))
        self.assertIn("title", response.json().get("properties"))
