import os
import shutil
import tempfile
from copy import deepcopy
from io import StringIO
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from mapentity.tests.factories import UserFactory, SuperUserFactory
from mapentity.views.generic import MapEntityList

from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.models import FileType, HDViewPoint
from geotrek.common.parsers import Parser
from geotrek.common.tasks import launch_sync_rando, import_datas
from geotrek.common.tests.factories import LicenseFactory, TargetPortalFactory
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

        dirs = list(settings_template[1]['DIRS'])
        self.temp_directory = tempfile.mkdtemp()
        shutil.copytree(os.path.join('geotrek', 'common', 'tests', 'data', 'templates_portal', 'trekking'),
                        os.path.join(self.temp_directory, 'trekking'))
        shutil.move(os.path.join(self.temp_directory, 'trekking', 'portal'),
                    os.path.join(self.temp_directory, 'trekking', f'portal_{self.portal_1.pk}'))
        dirs[0] = self.temp_directory
        new_dir_template = tuple(dirs)
        settings_template[1]['DIRS'] = new_dir_template
        return settings_template

    @mock.patch('mapentity.helpers.requests.get')
    def test_trek_document_portal(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.content = b'xxx'

        with override_settings(TEMPLATES=self.init_temp_directory()):
            response = self.client.get(reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk,
                                                                                  'slug': self.trek.slug,
                                                                                  }), {'portal': self.portal_1.pk})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name=f'trekking/portal_{self.portal_1.pk}/trek_public_pdf.css')
        self.assertTemplateUsed(response, template_name=f'trekking/portal_{self.portal_1.pk}/trek_public_pdf.html')
        self.assertTemplateUsed(response, template_name='trekking/trek_public_pdf.html')
        self.assertTemplateUsed(response, template_name='trekking/trek_public_pdf_base.html')

    @mock.patch('mapentity.helpers.requests.get')
    def test_trek_document_booklet_portal(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.content = b'xxx'

        with override_settings(TEMPLATES=self.init_temp_directory()):
            response = self.client.get(reverse('trekking:trek_booklet_printable',
                                               kwargs={'lang': 'fr', 'pk': self.trek.pk,
                                                       'slug': self.trek.slug,
                                                       }), {'portal': self.portal_1.pk})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                template_name=f'trekking/portal_{self.portal_1.pk}/trek_public_booklet_pdf.html')
        self.assertTemplateUsed(response, template_name='trekking/trek_public_booklet_pdf.html')
        self.assertTemplateUsed(response, template_name='trekking/trek_public_pdf_base.html')

    @mock.patch('mapentity.helpers.requests.get')
    def test_trek_document_wrong_portal(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.content = b'xxx'

        with override_settings(TEMPLATES=self.init_temp_directory()):
            response = self.client.get(reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk,
                                                                                  'slug': self.trek.slug,
                                                                                  }), {'portal': self.portal_2.pk})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, template_name=f'trekking/portal_{self.portal_1.pk}/trek_public_pdf.css')
        self.assertTemplateNotUsed(response, template_name=f'trekking/portal_{self.portal_1.pk}/trek_public_pdf.html')
        self.assertTemplateUsed(response, template_name='trekking/trek_public_pdf.html')
        self.assertTemplateUsed(response, template_name='trekking/trek_public_pdf_base.html')


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(username='homer', password='dooh')

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_settings_json(self):
        url = reverse('common:settings_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_check_extents(self):
        url = reverse('common:check_extents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(COLUMNS_LISTS={})
    @mock.patch('geotrek.common.mixins.views.logger')
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
        cls.user = UserFactory.create(username='homer', password='dooh')

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_import_form_access(self):
        url = reverse('common:import_dataset')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cities')

    def test_import_form_access_other_language(self):
        url = reverse('common:import_dataset')
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Communes')

    def test_import_update_access(self):
        url = reverse('common:import_update_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_from_file_good_zip_file(self):
        self.user.is_superuser = True
        self.user.save()

        with open('geotrek/common/tests/data/test.zip', 'rb') as real_archive:
            url = reverse('common:import_dataset')

            response_real = self.client.post(
                url, {
                    'upload-file': 'Upload',
                    'with-file-parser': '1',
                    'with-file-file': real_archive,
                    'with-file-encoding': 'UTF-8'
                }
            )
            self.assertEqual(response_real.status_code, 200)
            self.assertNotContains(response_real, "File must be of ZIP type.")

    @mock.patch('geotrek.common.tasks.current_task')
    @mock.patch('geotrek.common.tasks.import_datas.delay')
    def test_import_from_file_good_geojson_file(self, mocked, mocked_current_task):
        self.user.is_superuser = True
        self.user.save()
        FileType.objects.create(type="Photographie")
        mocked.side_effect = import_datas
        mocked_current_task.request.id = '1'
        with open('geotrek/common/tests/data/test.geojson', 'rb') as geojson:
            url = reverse('common:import_dataset')
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("id_with-file-file", resp.content.decode("utf-8"))
            response_real = self.client.post(
                url, {
                    'upload-file': 'Upload',
                    'with-file-parser': '4',
                    'with-file-file': geojson,
                    'with-file-encoding': 'UTF-8'
                }
            )
            self.assertEqual(response_real.status_code, 200)
        self.assertEqual(Trek.objects.count(), 1)

    @mock.patch('geotrek.common.tasks.import_datas.delay')
    def test_import_from_file_bad_file(self, mocked):
        self.user.is_superuser = True
        self.user.save()

        Parser.label = "Test"

        fake_archive = SimpleUploadedFile(
            "file.doc", b"file_content", content_type="application/msword")
        url = reverse('common:import_dataset')

        response_fake = self.client.post(
            url, {
                'upload-file': 'Upload',
                'with-file-parser': '1',
                'with-file-file': fake_archive,
                'with-file-encoding': 'UTF-8'
            }
        )
        self.assertEqual(response_fake.status_code, 200)
        self.assertEqual(mocked.call_count, 1)

        Parser.label = None

    def test_import_form_no_parser_no_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        real_archive = open('geotrek/common/tests/data/test.zip', 'rb+')
        url = reverse('common:import_dataset')

        response_real = self.client.post(
            url, {
                'upload-file': 'Upload',
                'with-file-parser': '1',
                'with-file-file': real_archive,
                'with-file-encoding': 'UTF-8'
            }
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertNotContains(response_real, '<form  method="post"')

    def test_import_from_web_bad_parser(self):
        self.user.is_superuser = True
        self.user.save()

        url = reverse('common:import_dataset')

        response_real = self.client.post(
            url, {
                'import-web': 'Upload',
                'without-file-parser': '99',
            }
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertContains(response_real, "Select a valid choice. 99 is not one of the available choices.")
        # There is no parser available for user not superuser

    def test_import_from_web_good_parser(self):
        self.user.is_superuser = True
        self.user.save()

        url = reverse('common:import_dataset')
        real_key = self.client.get(url).context['form_without_file'].fields['parser'].choices[0][0]
        response_real = self.client.post(
            url, {
                'import-web': 'Upload',
                'without-file-parser': real_key,
            }
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertNotContains(response_real, "Select a valid choice. {real_key} "
                                              "is not one of the available choices.".format(real_key=real_key))


class SyncRandoViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super_user = SuperUserFactory.create(username='admin', password='super')
        cls.simple_user = User.objects.create_user(username='homer', password='doooh')

    def setUp(self):
        if os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync')):
            shutil.rmtree(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'))

    def test_get_sync_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.get(reverse('common:sync_randos_view'))
        self.assertEqual(response.status_code, 200)

    def test_post_sync_superuser(self):
        """
        test if sync can be launched by superuser post
        """
        self.client.login(username='admin', password='super')
        response = self.client.post(reverse('common:sync_randos'), data={})
        self.assertRedirects(response, '/commands/syncview')

    def test_get_sync_simpleuser(self):
        self.client.login(username='homer', password='doooh')
        response = self.client.get(reverse('common:sync_randos_view'))
        self.assertRedirects(response, '/login/?next=/commands/syncview')

    def test_post_sync_simpleuser(self):
        """
        test if sync can be launched by simple user post
        """
        self.client.login(username='homer', password='doooh')
        response = self.client.post(reverse('common:sync_randos'), data={})
        self.assertRedirects(response, '/login/?next=/commands/sync')

    def test_get_sync_states_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.post(reverse('common:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def test_get_sync_states_simpleuser(self):
        self.client.login(username='homer', password='doooh')
        response = self.client.post(reverse('common:sync_randos_state'), data={})
        self.assertRedirects(response, '/login/?next=/commands/statesync/')

    @mock.patch('sys.stdout', new_callable=StringIO)
    @override_settings(CELERY_ALWAYS_EAGER=False,
                       SYNC_RANDO_ROOT=os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'),
                       SYNC_RANDO_OPTIONS={'url': 'http://localhost:8000',
                                           'skip_tiles': True, 'skip_pdf': True,
                                           'skip_dem': True, 'skip_profile_png': True})
    def test_get_sync_rando_states_superuser_with_sync_rando(self, mocked_stdout):
        if os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync')):
            shutil.rmtree(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'))
        self.client.login(username='admin', password='super')
        launch_sync_rando.apply()
        response = self.client.post(reverse('common:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"infos": "Sync ended"', response.content)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('geotrek.common.management.commands.sync_rando.Command.handle', return_value=None,
                side_effect=Exception('This is a test'))
    @override_settings(CELERY_ALWAYS_EAGER=False,
                       SYNC_RANDO_ROOT=os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'),
                       SYNC_RANDO_OPTIONS={'url': 'http://localhost:8000',
                                           'skip_tiles': True, 'skip_pdf': True,
                                           'skip_dem': True, 'skip_profile_png': True})
    def test_get_sync_rando_states_superuser_with_sync_mobile_fail(self, mocked_stdout, command):
        self.client.login(username='admin', password='super')
        launch_sync_rando.apply()
        response = self.client.post(reverse('common:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"exc_message": "This is a test"', response.content)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('landez.TilesManager.tile', return_value=b'I am a png')
    @override_settings(SYNC_RANDO_ROOT=os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'),
                       SYNC_RANDO_OPTIONS={'url': 'http://localhost:8000', 'skip_tiles': False,
                                           'skip_pdf': False,
                                           'skip_dem': False, 'skip_profile_png': False})
    def test_launch_sync_rando(self, mock_tile, mock_map_image, mocked_stdout):
        task = launch_sync_rando.apply()
        log = mocked_stdout.getvalue()
        self.assertIn("Done", log)
        self.assertEqual(task.status, "SUCCESS")

    @mock.patch('geotrek.common.management.commands.sync_rando.Command.handle', return_value=None,
                side_effect=Exception('This is a test'))
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_launch_sync_rando_fail(self, mocked_stdout, command):
        task = launch_sync_rando.apply()
        log = mocked_stdout.getvalue()
        self.assertNotIn("Done", log)
        self.assertNotIn('Sync ended', log)
        self.assertEqual(task.status, "FAILURE")

    @mock.patch('geotrek.common.management.commands.sync_rando.Command.handle', return_value=None,
                side_effect=Exception('This is a test'))
    @override_settings(SYNC_RANDO_ROOT=os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'))
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_launch_sync_rando_no_rando_root(self, mocked_stdout, command):
        if os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync')):
            shutil.rmtree(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'))
        task = launch_sync_rando.apply()
        log = mocked_stdout.getvalue()
        self.assertNotIn("Done", log)
        self.assertNotIn('Sync rando ended', log)
        self.assertEqual(task.status, "FAILURE")

    def tearDown(self):
        if os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando')):
            shutil.rmtree(os.path.join(settings.TMP_DIR, 'sync_rando'))


class HDViewPointViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.su = SuperUserFactory.create()
        cls.trek = TrekFactory()
        cls.license = LicenseFactory()

    def setUp(self):
        self.client.force_login(user=self.su)

    def test_crud_view(self):
        # Test create view
        ContentType.objects.clear_cache()  # Sometimes cache can contain bad values
        response = self.client.get('%s?object_id=%s&content_type=%s' % (HDViewPoint.get_add_url(),
                                                                        self.trek.pk,
                                                                        ContentType.objects.get_for_model(Trek).pk
                                                                        )
                                   )
        self.assertEqual(response.status_code, 200)
        img = SimpleUploadedFile("an_uploaded_image.png", b"file_content", content_type="image/x-png")
        data = {
            'picture': img,
            'title': "Un titre",
            'author': "Someone",
            'legend': "Something",
            'geom': "SRID=2154;POINT(0 0)",
            "license": self.license.pk
        }
        response = self.client.post('%s?object_id=%s&content_type=%s' % (HDViewPoint.get_add_url(),
                                                                         self.trek.pk,
                                                                         ContentType.objects.get_for_model(Trek).pk
                                                                         ),
                                    data)
        vp = HDViewPoint.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.trek, vp.content_object)
        self.assertIn("an_uploaded_image", vp.picture.name)
        self.assertEqual(vp.title, "Un titre")
        self.assertEqual(vp.author, "Someone")
        self.assertEqual(vp.legend, "Something")
        self.assertEqual(vp.license, self.license)
        self.assertEqual(vp.geom, Point((0, 0), srid=2154))
        # TODO assert annotations

        # Test Update view
        response = self.client.get(vp.get_update_url())
        self.assertEqual(response.status_code, 200)
        img = SimpleUploadedFile("an_uploaded_image.png", b"file_content", content_type="image/x-png")
        data = {
            'picture': img,
            'title': "Un titre",
            'author': "Someone",
            'legend': "Something else",
            'geom': "SRID=2154;POINT(0 0)"
        }
        response = self.client.post(vp.get_update_url(), data)
        self.assertRedirects(response, f"/hdviewpoint/{vp.pk}", status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        vp = HDViewPoint.objects.first()
        self.assertEqual(vp.legend, "Something else")
        self.assertEqual(vp.license, None)

        # Test delete view
        vp = HDViewPoint.objects.first()
        response = self.client.post(vp.get_delete_url(), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(HDViewPoint.objects.count(), 0)
