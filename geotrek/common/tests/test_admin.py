from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from geotrek.common.factories import AttachmentFactory
from geotrek.common.models import Attachment, FileType
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.trekking.factories import POIFactory, TrekFactory

from mapentity.factories import SuperUserFactory


class AttachmentAdminTest(TestCase):
    def setUp(self):
        self.user = SuperUserFactory.create(password='booh')
        self.content = POIFactory.create(geom='SRID=%s;POINT(1 1)' % settings.SRID)

        self.picture = AttachmentFactory(content_object=self.content,
                                         attachment_file=get_dummy_uploaded_image(), )
        self.trek = TrekFactory.create(geom='SRID=%s;LINESTRING(0 0, 1 0, 2 0)' % settings.SRID)
        self.picture_2 = AttachmentFactory(content_object=self.trek,
                                           attachment_file=get_dummy_uploaded_image(), )

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_changelist_attachment(self):
        self.login()
        list_url = reverse('admin:common_attachment_changelist')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Attachment.objects.get(pk=self.picture.pk).title)
        self.assertContains(response, Attachment.objects.get(pk=self.picture_2.pk).title)

    def test_changelist_attachment_filter_content_id(self):
        self.login()
        list_url = reverse('admin:common_attachment_changelist')
        data = {
            'content_type': ContentType.objects.get(model='poi').pk
        }

        response = self.client.get(list_url, data)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, Attachment.objects.get(pk=self.picture.pk).title)
        self.assertNotContains(response, Attachment.objects.get(pk=self.picture_2.pk).title)

    def test_attachment_can_be_change(self):
        self.login()
        change_url = reverse('admin:common_attachment_change', args=[self.picture.pk])
        file_type = FileType.objects.first()
        response = self.client.post(change_url, {'title': 'Coucou', 'filetype': file_type.pk, 'starred': True})
        self.assertEqual(response.status_code, 302)
        attachment_modified = Attachment.objects.get(pk=self.picture.pk)
        self.assertEqual(attachment_modified.title, self.picture.title)
        # Is not changed depend on file title
        self.assertEqual(attachment_modified.starred, True)
        self.assertEqual(response.url, reverse('admin:common_attachment_changelist'))
