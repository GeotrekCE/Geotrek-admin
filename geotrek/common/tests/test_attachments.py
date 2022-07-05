from unittest import mock


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

from mapentity.tests.factories import SuperUserFactory, UserFactory
from geotrek.common.models import AccessibilityAttachment, Attachment
from geotrek.common.tests.factories import AttachmentAccessibilityFactory, FileTypeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.trekking.tests.factories import TrekFactory, PracticeFactory
from geotrek.trekking.views import TrekDetail


def add_url_for_obj(obj):
    return reverse('add_attachment_accessibility', kwargs={
        'app_label': obj._meta.app_label,
        'model_name': obj._meta.model_name,
        'pk': obj.pk
    })


def update_url_for_obj(attachment):
    return reverse('update_attachment_accessibility', kwargs={
        'attachment_pk': attachment.pk
    })


def delete_url_for_obj(attachment):
    return reverse('delete_attachment_accessibility', kwargs={
        'attachment_pk': attachment.pk
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
            'attachment_accessibility_file': get_dummy_uploaded_image(),
            'info_accessibility': 'slope'
        }
        return AccessibilityAttachment.objects.create(**kwargs)

    def createAttachment(self, obj):
        kwargs = {
            'content_type': ContentType.objects.get_for_model(obj),
            'object_id': obj.pk,
            'filetype_id': FileTypeFactory.create().pk,
            'creator': self.user,
            'title': "Attachment title",
            'legend': "Attachment legend",
            'attachment_file': get_dummy_uploaded_image(),
        }
        return Attachment.objects.create(**kwargs)

    def test_list_attachments_in_details(self):
        self.createAttachmentAccessibility(self.object)
        self.user.user_permissions.add(Permission.objects.get(codename='read_trek'))
        self.user.user_permissions.add(Permission.objects.get(codename='read_attachment'))
        self.client.force_login(self.user)
        response = self.client.get(self.object.get_detail_url())

        html = response.content
        self.assertTemplateUsed(response, template_name='common/attachment_list.html')
        self.assertTemplateUsed(response, template_name='common/attachment_accessibility_list.html')

        self.assertEqual(1, len(AccessibilityAttachment.objects.attachments_for_object(self.object)))

        self.assertNotIn(b"Submit attachment", html)

        for attachment in AccessibilityAttachment.objects.attachments_for_object(self.object):
            self.assertIn(attachment.legend.encode(), html)
            self.assertIn(attachment.title.encode(), html)
            self.assertIn(attachment.attachment_accessibility_file.url.encode(), html)
            self.assertIn(b'paperclip/fileicons/odt.png', html)

    @override_settings(ACCESSIBILITY_ATTACHMENTS_ENABLED=False)
    def test_list_attachments_not_in_details_attachments_accessibility_disabled(self):
        self.createAttachmentAccessibility(self.object)
        self.user.user_permissions.add(Permission.objects.get(codename='read_trek'))
        self.user.user_permissions.add(Permission.objects.get(codename='read_attachment'))
        self.client.force_login(self.user)
        response = self.client.get(self.object.get_detail_url())

        self.assertTemplateUsed(response, template_name='common/attachment_list.html')
        self.assertTemplateNotUsed(response, template_name='common/attachment_accessibility_list.html')

    def test_add_form_in_details_if_perms(self):
        self.user.has_perm = mock.MagicMock(return_value=True)
        view = TrekDetail.as_view()
        request = self.createRequest()
        response = view(request, pk=self.object.pk)
        html = response.render()
        self.assertIn(b"Submit attachment", html.content)
        self.assertIn(
            '<form  action="/trekking/add-accessibility-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
            html.content)

    def test_update_form_in_details_if_perms(self):
        self.user.has_perm = mock.MagicMock(return_value=True)
        AttachmentAccessibilityFactory.create(content_object=self.object)
        view = TrekDetail.as_view()
        request = self.createRequest()
        response = view(request, pk=self.object.pk)
        html = response.render()
        self.assertIn(b"Submit attachment", html.content)
        self.assertIn(
            '<form  action="/trekking/add-accessibility-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
            html.content)
        self.assertIn(
            '<form  action="/paperclip/add-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
            html.content)

    def test_create_attachments_accessibility_object_other_structure(self):
        def user_perms(p):
            return {'authent.can_bypass_structure': False}.get(p, True)
        self.createAttachmentAccessibility(self.object)
        user = UserFactory()
        user.has_perm = mock.MagicMock(side_effect=user_perms)
        user.user_permissions.add(Permission.objects.get(codename='read_trek'))
        user.user_permissions.add(Permission.objects.get(codename='read_attachment'))
        self.client.force_login(user)
        response = self.client.get(self.object.get_detail_url())

        html = response.content
        self.assertTemplateUsed(response, template_name='common/attachment_list.html')
        self.assertTemplateNotUsed(response, template_name='common/_attachment_table.html')
        self.assertTemplateUsed(response, template_name='common/attachment_accessibility_list.html')

        self.assertNotIn(b"Submit attachment", html)
        self.assertNotIn(
            '<form  action="/trekking/add-accessibility-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
            html)
        self.assertIn(b"You are not allowed to modify attachments on this object, this object is not from the same structure.", html)

    def test_create_attachments_object_other_structure(self):
        def user_perms(p):
            return {'authent.can_bypass_structure': False}.get(p, True)
        self.createAttachment(self.object)
        user = UserFactory()
        user.has_perm = mock.MagicMock(side_effect=user_perms)
        user.user_permissions.add(Permission.objects.get(codename='read_trek'))
        user.user_permissions.add(Permission.objects.get(codename='read_attachment'))
        self.client.force_login(user)
        response = self.client.get(self.object.get_detail_url())

        html = response.content
        self.assertTemplateUsed(response, template_name='common/attachment_list.html')
        self.assertTemplateNotUsed(response, template_name='common/_attachment_table.html')
        self.assertTemplateUsed(response, template_name='common/attachment_accessibility_list.html')

        self.assertNotIn(b"Submit attachment", html)
        self.assertNotIn(
            '<form  action="/trekking/add-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
            html)
        self.assertIn(b"You are not allowed to modify attachments on this object, this object is not from the same structure.", html)


class UploadAddAttachmentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.object = TrekFactory.create()

    def setUp(self):
        self.client.force_login(user=self.user)

    def attachmentPostData(self):
        data = {
            'creator': self.user,
            'title': "A title",
            'legend': "A legend",
            'attachment_accessibility_file': get_dummy_uploaded_image(name='face.jpg'),
            'info_accessibility': 'slope'
        }
        return data

    def test_upload_redirects_to_trek_detail_url(self):
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


class UploadUpdateAttachmentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.object = TrekFactory.create()
        cls.attachment = AttachmentAccessibilityFactory.create(content_object=cls.object)

    def setUp(self):
        self.client.force_login(user=self.user)

    def attachmentPostData(self):
        data = {
            'creator': self.user,
            'title': "A title",
            'legend': "A legend",
            'attachment_accessibility_file': get_dummy_uploaded_image(name='face.jpg'),
            'info_accessibility': 'slope'
        }
        return data

    def test_get_update_url(self):
        response = self.client.get(update_url_for_obj(self.attachment))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="Update attachment"', response.content)

    def test_post_update_url(self):
        response = self.client.post(update_url_for_obj(self.attachment),
                                    data=self.attachmentPostData())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object.get_detail_url()}?tab=attachments-accessibility")
        self.attachment.refresh_from_db()
        self.assertEqual(self.attachment.legend, "A legend")


class UploadDeleteAttachmentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.object = TrekFactory.create()
        cls.attachment = AttachmentAccessibilityFactory.create(content_object=cls.object)

    def test_get_delete_with_perms_url(self):
        self.user = SuperUserFactory.create()
        self.client.force_login(user=self.user)
        response = self.client.get(delete_url_for_obj(self.attachment))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object.get_detail_url()}?tab=attachments-accessibility")
        self.assertEqual(0, AccessibilityAttachment.objects.count())

    @mock.patch('django.contrib.auth.models.PermissionsMixin.has_perm')
    def test_get_delete_without_perms_url(self, mocke):
        def user_perms(p, obj=None):
            return {'common.delete_attachment_others': False}.get(p, True)
        self.user = UserFactory()
        mocke.side_effect = user_perms
        self.client.force_login(user=self.user)
        response = self.client.get(delete_url_for_obj(self.attachment))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object.get_detail_url()}?tab=attachments-accessibility")
        self.assertEqual(1, AccessibilityAttachment.objects.count())
        response = self.client.get(delete_url_for_obj(self.attachment), follow=True)
        self.assertIn(b'You are not allowed to delete this attachment.', response.content)


class ModelAttachmentAccessibilityTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.object = TrekFactory.create(name="iul")
        cls.attachment = AttachmentAccessibilityFactory.create(attachment_accessibility_file=get_dummy_uploaded_image(name="bar.png"),
                                                               creator=UserFactory(username='foo'),
                                                               content_object=cls.object,
                                                               title="")

    def test_str(self):
        self.assertEqual(f"foo attached {self.attachment.attachment_accessibility_file}", str(self.attachment))


class ServeAttachmentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(username='foo')
        cls.superuser = SuperUserFactory(username='bar')
        cls.object = TrekFactory.create(published=False, name="iul")
        cls.attachment = AttachmentAccessibilityFactory.create(attachment_accessibility_file=get_dummy_uploaded_image(name="bar.png"),
                                                               creator=cls.user,
                                                               content_object=cls.object,
                                                               title="")

    def test_get_attachment_without_authenticated(self):
        response = self.client.get(self.attachment.attachment_accessibility_file.url)
        self.assertEqual(response.status_code, 403)

    def test_get_attachment_without_permission_read_attachment(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.attachment.attachment_accessibility_file.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch('django.contrib.auth.models.PermissionsMixin.has_perm')
    def test_get_attachment_without_permission_read_object(self, mocke):
        def user_perms(p, obj=None):
            return {'common.read_attachment': True}.get(p, False)
        mocke.side_effect = user_perms
        self.client.force_login(user=self.user)
        response = self.client.get(self.attachment.attachment_accessibility_file.url)
        self.assertEqual(response.status_code, 403)

    def test_get_attachment_do_not_exist(self):
        response = self.client.get(f'/media/attachments_accessibility/trekking_trek/{self.object.pk}/doesnotexist.png')
        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=False)
    def test_get_attachment_without_debug(self):
        self.client.force_login(user=self.superuser)
        response = self.client.get(self.attachment.attachment_accessibility_file.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_get_attachment_with_debug(self):
        self.client.force_login(user=self.superuser)
        response = self.client.get(self.attachment.attachment_accessibility_file.url)
        self.assertEqual(response.status_code, 200)

    def test_get_attachment_on_model_without_generic(self):
        obj = PracticeFactory.create()
        attachment = AttachmentAccessibilityFactory.create(attachment_accessibility_file=get_dummy_uploaded_image(name="bar.png"),
                                                           creator=self.user,
                                                           content_object=obj,
                                                           title="")
        self.client.force_login(user=self.superuser)
        response = self.client.get(attachment.attachment_accessibility_file.url)
        self.assertEqual(response.status_code, 404)
