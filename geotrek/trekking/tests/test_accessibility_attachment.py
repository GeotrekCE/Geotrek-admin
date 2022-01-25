from unittest import mock


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase, RequestFactory
from django.urls import reverse

from mapentity.tests.factories import SuperUserFactory, UserFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.trekking.tests.factories import TrekFactory
from geotrek.trekking.models import AccessibilityAttachment
from geotrek.trekking.views import TrekDetail


def add_url_for_obj(obj):
    return reverse('add_attachment_accessibility', kwargs={
        'app_label': obj._meta.app_label,
        'model_name': obj._meta.model_name,
        'pk': obj.pk
    })


class EntityAttachmentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        def user_perms(p):
            return {'paperclip.add_attachment': False}.get(p, True)
        cls.user = UserFactory()
        cls.user.has_perm = mock.MagicMock(side_effect=user_perms)
        cls.object = TrekFactory.create()
        call_command('update_permissions_mapentity', verbosity=0)

    def createRequest(self):
        request = RequestFactory().get('/')
        request.session = {}
        request.user = self.user
        return request

    def createAttachmentAccessibility(self, obj):
        kwargs = {
            'content_type': ContentType.objects.get_for_model(obj),
            'object_id': obj.pk,
            'creator': self.user,
            'title': "Attachment title",
            'legend': "Attachment legend",
            'attachment_accessibility_file': get_dummy_uploaded_image()
        }
        return AccessibilityAttachment.objects.create(**kwargs)

    def test_list_attachments_in_details(self):
        self.createAttachmentAccessibility(self.object)
        self.user.user_permissions.add(Permission.objects.get(codename='read_trek'))
        self.user.user_permissions.add(Permission.objects.get(codename='read_attachment'))
        self.client.force_login(self.user)
        response = self.client.get(self.object.get_detail_url())

        html = response.content
        self.assertTemplateUsed(response, template_name='paperclip/attachment_list.html')
        self.assertTemplateUsed(response, template_name='trekking/attachment_accessibility_list.html')

        self.assertEqual(1, len(AccessibilityAttachment.objects.attachments_for_object(self.object)))

        self.assertNotIn(b"Submit attachment", html)

        for attachment in AccessibilityAttachment.objects.attachments_for_object(self.object):
            self.assertIn(attachment.legend.encode(), html)
            self.assertIn(attachment.title.encode(), html)
            self.assertIn(attachment.attachment_accessibility_file.url.encode(), html)
            self.assertIn(b'paperclip/fileicons/odt.png', html)

    def test_form_in_details_if_perms(self):
        self.user.has_perm = mock.MagicMock(return_value=True)
        view = TrekDetail.as_view()
        request = self.createRequest()
        response = view(request, pk=self.object.pk)
        html = response.render()
        self.assertIn(b"Submit attachment", html.content)
        self.assertIn(
            '<form  action="/trekking/add-accessibility-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
            html.content)


class UploadAttachmentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create(password='booh')
        cls.object = TrekFactory.create()

    def setUp(self):
        self.client.force_login(user=self.user)

    def attachmentPostData(self):
        data = {
            'creator': self.user,
            'title': "A title",
            'legend': "A legend",
            'attachment_accessibility_file': get_dummy_uploaded_image(name='face.jpg')
        }
        return data

    def test_upload_redirects_to_dummy_detail_url(self):
        response = self.client.post(add_url_for_obj(self.object),
                                    data=self.attachmentPostData())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object.get_detail_url()}?tab=attachments-accessibility")

    def test_upload_creates_attachment(self):
        data = self.attachmentPostData()
        self.client.post(add_url_for_obj(self.object), data=data)
        att = AccessibilityAttachment.objects.attachments_for_object(self.object).get()
        self.assertEqual(att.title, data['title'])
        self.assertEqual(att.legend, data['legend'])

    def test_title_gives_name_to_file(self):
        data = self.attachmentPostData()
        self.client.post(add_url_for_obj(self.object), data=data)
        att = AccessibilityAttachment.objects.attachments_for_object(self.object).get()
        self.assertTrue('a-title' in att.attachment_accessibility_file.name)

    def test_filename_is_used_if_no_title(self):
        data = self.attachmentPostData()
        data['title'] = ''
        self.client.post(add_url_for_obj(self.object), data=data)
        att = AccessibilityAttachment.objects.attachments_for_object(self.object).get()
        self.assertTrue('face' in att.attachment_accessibility_file.name)
