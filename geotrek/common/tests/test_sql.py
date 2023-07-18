import os
import shutil
from tempfile import NamedTemporaryFile
from unittest import mock
from django.test import TestCase

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection

from geotrek.common.models import AccessibilityAttachment, Attachment, Label, TargetPortal
from geotrek.common.tests.factories import FileTypeFactory
from geotrek.common.utils.postgresql import load_sql_files
from geotrek.trekking.tests.factories import TrekFactory
from geotrek.authent.tests.factories import UserFactory


class SQLDefaultValuesTest(TestCase):
    def test_accessibilityattachment(self):
        trek = TrekFactory.create()
        user = UserFactory.create()
        ct = ContentType.objects.get_by_natural_key('trekking', 'trek')
        with connection.cursor() as cur:
            cur.execute(f"""INSERT INTO common_accessibilityattachment
                           (
                           attachment_accessibility_file,
                           content_type_id,
                           object_id,
                           creator_id,
                           random_suffix
                           ) VALUES
                           (
                           'attachments_accessibility/trekking_trek/1/foo.png',
                           {ct.pk},
                           {trek.pk},
                           {user.pk},
                           '')""")
        accessibility_attachment = AccessibilityAttachment.objects.first()
        self.assertEqual(accessibility_attachment.author,
                         '')

    def test_attachment(self):
        trek = TrekFactory.create()
        user = UserFactory.create()
        filetype = FileTypeFactory.create()
        ct = ContentType.objects.get_by_natural_key('trekking', 'trek')
        with connection.cursor() as cur:
            cur.execute(f"""INSERT INTO common_attachment
                                   (
                                   attachment_file,
                                   content_type_id,
                                   object_id,
                                   creator_id,
                                   filetype_id,
                                   random_suffix
                                   ) VALUES
                                   (
                                   'attachments/trekking_trek/1/foo.png',
                                   {ct.pk},
                                   {trek.pk},
                                   {user.pk},
                                   {filetype.pk},
                                   '')""")
        attachment = Attachment.objects.first()
        self.assertEqual(attachment.author, '')

    def test_target_portal(self):
        with connection.cursor() as cur:
            cur.execute("""INSERT INTO common_targetportal
                                   (
                                   name,
                                   website
                                   ) VALUES
                                   (
                                   'name_target',
                                   'http://foo.com'
                                   )""")
        target_portal = TargetPortal.objects.first()
        self.assertEqual(target_portal.facebook_image_url, '/images/logo-geotrek.png')

    def test_label(self):
        with connection.cursor() as cur:
            cur.execute("""INSERT INTO common_label
                                   (
                                   name
                                   ) VALUES
                                   (
                                   'name_label'
                                   )""")
        label = Label.objects.first()
        self.assertFalse(label.filter)


class ExtraSQLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not os.path.exists(os.path.join(settings.VAR_DIR, 'conf', 'extra_sql')):
            os.mkdir(os.path.join(settings.VAR_DIR, 'conf', 'extra_sql'))
            os.mkdir(os.path.join(settings.VAR_DIR, 'conf', 'extra_sql', 'common'))

    def test_custom_sql(self):

        tmp_file = NamedTemporaryFile(suffix='.sql', prefix='test_', mode='w+',
                                      dir=os.path.join(settings.VAR_DIR, 'conf', 'extra_sql', 'common'))
        tmp_file.write("""
        CREATE FUNCTION {{ schema_geotrek }}.test() RETURNS char SECURITY DEFINER AS $$
        BEGIN
            RETURN 'test';
        END;
        $$ LANGUAGE plpgsql;
        """)
        tmp_file.flush()
        common = apps.get_app_config('common')
        load_sql_files(common, 'test')
        tmp_file.close()

        cursor = connection.cursor()
        cursor.execute("""
        SELECT public.test();
        """)
        result = cursor.fetchall()
        tmp_file.close()
        self.assertEqual(result[0][0], 'test')

    @mock.patch('geotrek.common.utils.postgresql.logger')
    @mock.patch('traceback.print_exc')
    def test_failed_custom_sql(self, mock_traceback, mocked):
        tmp_file = NamedTemporaryFile(suffix='.sql', prefix='test_', mode='w+',
                                      dir=os.path.join(settings.VAR_DIR, 'conf', 'extra_sql', 'common'))
        tmp_file.write("""
        ERROR SQL
        """)
        tmp_file.flush()
        common = apps.get_app_config('common')
        with self.assertRaisesRegex(Exception, 'syntax error at or near "ERROR"'):
            load_sql_files(common, 'test')
        mocked.critical.assert_called_once_with(f"""Failed to install custom SQL file '{tmp_file.name}': syntax error at or near "ERROR"\nLINE 2:         ERROR SQL\n                ^\n\n""")
        tmp_file.close()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(os.path.join(settings.VAR_DIR, 'conf', 'extra_sql'))
