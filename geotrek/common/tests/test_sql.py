import os
import shutil
from tempfile import NamedTemporaryFile
from unittest import mock

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import TestCase

from geotrek.authent.tests.factories import UserFactory
from geotrek.common.models import (
    AccessibilityAttachment,
    Attachment,
    Label,
)
from geotrek.common.tests.factories import FileTypeFactory
from geotrek.common.utils.postgresql import load_sql_files
from geotrek.trekking.tests.factories import TrekFactory


class SQLDefaultValuesTest(TestCase):
    def test_accessibilityattachment(self):
        trek = TrekFactory.create()
        user = UserFactory.create()
        ct = ContentType.objects.get_by_natural_key("trekking", "trek")
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
        self.assertEqual(accessibility_attachment.author, "")

    def test_attachment(self):
        trek = TrekFactory.create()
        user = UserFactory.create()
        filetype = FileTypeFactory.create()
        ct = ContentType.objects.get_by_natural_key("trekking", "trek")
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
        self.assertEqual(attachment.author, "")

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
        if not os.path.exists(os.path.join(settings.VAR_DIR, "conf", "extra_sql")):
            os.mkdir(os.path.join(settings.VAR_DIR, "conf", "extra_sql"))
            os.mkdir(os.path.join(settings.VAR_DIR, "conf", "extra_sql", "common"))

    def test_custom_sql(self):
        tmp_file = NamedTemporaryFile(
            suffix=".sql",
            prefix="test_",
            mode="w+",
            dir=os.path.join(settings.VAR_DIR, "conf", "extra_sql", "common"),
        )
        tmp_file.write("""
        CREATE FUNCTION {{ schema_geotrek }}.test() RETURNS char SECURITY DEFINER AS $$
        BEGIN
            RETURN 'test';
        END;
        $$ LANGUAGE plpgsql;
        """)
        tmp_file.flush()
        common = apps.get_app_config("common")
        load_sql_files(common, "test")
        tmp_file.close()

        cursor = connection.cursor()
        cursor.execute("""
        SELECT public.test();
        """)
        result = cursor.fetchall()
        tmp_file.close()
        self.assertEqual(result[0][0], "test")

    @mock.patch("traceback.print_exc")
    def test_failed_custom_sql(self, mock_traceback):
        with self.assertLogs("geotrek.common.utils.postgresql", "CRITICAL") as cm:
            tmp_file = NamedTemporaryFile(
                suffix=".sql",
                prefix="test_",
                mode="w+",
                dir=os.path.join(settings.VAR_DIR, "conf", "extra_sql", "common"),
            )
            tmp_file.write("""
            ERROR SQL
            """)
            tmp_file.flush()
            common = apps.get_app_config("common")
            with self.assertRaisesRegex(Exception, 'syntax error at or near "ERROR"'):
                load_sql_files(common, "test")
            self.assertTrue(
                f"Failed to install custom SQL file '{tmp_file.name}': syntax error at or near \"ERROR\""
                in cm.output[0]
            )
            tmp_file.close()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(os.path.join(settings.VAR_DIR, "conf", "extra_sql"))
