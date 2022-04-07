from django.test import TestCase

from django.contrib.contenttypes.models import ContentType
from django.db import connection

from geotrek.common.models import AccessibilityAttachment, Attachment, Label, TargetPortal
from geotrek.common.tests.factories import FileTypeFactory
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
                           creator_id
                           ) VALUES
                           (
                           'attachments_accessibility/trekking_trek/1/foo.png',
                           {ct.pk},
                           {trek.pk},
                           {user.pk}
                           )""")
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
                                   filetype_id
                                   ) VALUES
                                   (
                                   'attachments/trekking_trek/1/foo.png',
                                   {ct.pk},
                                   {trek.pk},
                                   {user.pk},
                                   {filetype.pk}
                                   )""")
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
