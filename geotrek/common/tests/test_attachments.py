import os
from io import BytesIO
from unittest import mock

from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory, UserFactory
from paperclip.models import random_suffix_regexp
from PIL import Image

from geotrek.authent.tests.factories import StructureFactory
from geotrek.common.models import AccessibilityAttachment
from geotrek.common.tests.factories import (AttachmentAccessibilityFactory,
                                            AttachmentFactory)
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.trekking.tests.factories import PracticeFactory, TrekFactory
from geotrek.trekking.views import TrekDetail


def add_url_for_obj(obj):
    return reverse('common:add_attachment_accessibility', kwargs={
        'app_label': obj._meta.app_label,
        'model_name': obj._meta.model_name,
        'pk': obj.pk
    })


def update_url_for_obj(attachment):
    return reverse('common:update_attachment_accessibility', kwargs={
        'attachment_pk': attachment.pk
    })


def delete_url_for_obj(attachment):
    return reverse('common:delete_attachment_accessibility', kwargs={
        'attachment_pk': attachment.pk
    })


class EntityAttachmentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        def user_perms(p):
            return {'paperclip.add_attachment': False}.get(p, True)
        cls.user = UserFactory()
        cls.user.has_perm = mock.MagicMock(side_effect=user_perms)
        cls.object = TrekFactory.create(structure=StructureFactory(name="Another structure"))
        call_command('update_permissions_mapentity', verbosity=0)

    def createRequest(self):
        request = RequestFactory().get('/')
        request.session = {}
        request.user = self.user
        return request

    def createAttachmentAccessibility(self, obj):
        return AttachmentAccessibilityFactory(content_object=obj, creator=self.user)

    def createAttachment(self, obj):
        return AttachmentFactory(content_object=obj, creator=self.user)

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
            '<form  action="/add-accessibility-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
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
            '<form  action="/add-accessibility-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
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
            '<form  action="/add-accessibility-for/trekking/trek/{}/"'.format(self.object.pk).encode(),
            html)
        self.assertIn(b"You are not allowed to modify attachments on this object, this object is not from the same structure.", html)

    def test_filename_generation(self):
        # Prepare attachment
        file = BytesIO(b"File content")
        file.name = 'foo_file.txt'
        file.seek(0)
        attachment = AccessibilityAttachment.objects.create(content_object=self.object,
                                                            creator=self.user,
                                                            author="foo author",
                                                            legend="foo legend")
        # Assert filename and suffix are not computed if there is no file in attachment
        self.assertIsNone(attachment.prepare_file_suffix())
        # Assert filename is made of attachment file name plus random suffix
        attachment.attachment_accessibility_file = SimpleUploadedFile(
            file.name,
            file.read(),
            content_type='text/plain'
        )
        name_1 = attachment.prepare_file_suffix()
        regexp = random_suffix_regexp()
        self.assertRegex(attachment.random_suffix, regexp)
        new_name = f"foo_file{attachment.random_suffix}.txt"
        self.assertEqual(name_1, new_name)
        # Assert filename would be made of basename argument plus random suffix
        attachment.random_suffix = None
        name_4 = attachment.prepare_file_suffix("basename.txt")
        self.assertRegex(attachment.random_suffix, regexp)
        new_name = f"basename{attachment.random_suffix}.txt"
        self.assertEqual(name_4, new_name)
        # Assert filename is made of attachment title plus random suffix
        attachment.title = "foo_title"
        attachment.save(**{'force_refresh_suffix': True})
        self.assertRegex(attachment.random_suffix, regexp)
        new_name = f"foo_title{attachment.random_suffix}.txt"
        _, name_2 = os.path.split(attachment.attachment_accessibility_file.name)
        self.assertEqual(name_2, new_name)
        name_3 = attachment.prepare_file_suffix()
        self.assertEqual(new_name, name_3)

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


class SetUpTestDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.superuser = SuperUserFactory.create()
        cls.object = TrekFactory.create()
        cls.user = UserFactory()
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            cls.user.user_permissions.add(perm.pk)
        cls.attachment = AttachmentAccessibilityFactory.create(content_object=cls.object)
        cls.object_other_structure = TrekFactory.create(structure=StructureFactory.create())
        cls.attachment_other_structure = AttachmentAccessibilityFactory.create(content_object=cls.object_other_structure)


class UploadAddAttachmentTestCase(SetUpTestDataMixin, TestCase):

    def setUp(self):
        self.client.force_login(user=self.superuser)

    def attachmentPostData(self):
        data = {
            'creator': self.superuser,
            'title': "A title",
            'legend': "A legend",
            'attachment_accessibility_file': get_dummy_uploaded_image(name='face.png'),
            'info_accessibility': 'slope',
            'next': f"{self.object.get_detail_url()}?tab=attachments"
        }
        return data

    def test_upload_redirects_to_trek_detail_url(self):
        response = self.client.post(add_url_for_obj(self.object),
                                    data=self.attachmentPostData())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object.get_detail_url()}?tab=attachments")
        self.assertEqual(3, AccessibilityAttachment.objects.count())

        self.client.force_login(user=self.user)
        response = self.client.post(add_url_for_obj(self.object_other_structure),
                                    data=self.attachmentPostData())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object_other_structure.get_detail_url()}")
        self.assertEqual(3, AccessibilityAttachment.objects.count())

    def test_upload_creates_attachment(self):
        data = self.attachmentPostData()
        self.client.post(add_url_for_obj(self.object), data=data)
        att = AccessibilityAttachment.objects.attachments_for_object(self.object).get(title="A title")
        self.assertEqual(att.title, data['title'])
        self.assertEqual(att.legend, data['legend'])

    def test_title_gives_name_to_file(self):
        data = self.attachmentPostData()
        self.client.post(add_url_for_obj(self.object), data=data)
        att = AccessibilityAttachment.objects.attachments_for_object(self.object).get(title="A title")
        self.assertTrue('a-title' in att.attachment_accessibility_file.name)

    def test_filename_is_used_if_no_title(self):
        data = self.attachmentPostData()
        data['title'] = ''
        self.client.post(add_url_for_obj(self.object), data=data)
        att = AccessibilityAttachment.objects.attachments_for_object(self.object).get(title="")
        self.assertTrue('face' in att.attachment_accessibility_file.name)


class UploadUpdateAttachmentTestCase(SetUpTestDataMixin, TestCase):

    def attachmentPostData(self):
        data = {
            'creator': self.user,
            'title': "A title",
            'legend': "A legend",
            'attachment_accessibility_file': get_dummy_uploaded_image(name='face.png'),
            'info_accessibility': 'slope',
            'next': f"{self.object.get_detail_url()}?tab=attachments"
        }
        return data

    def test_get_update_url(self):
        self.client.force_login(user=self.superuser)
        response = self.client.get(update_url_for_obj(self.attachment))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="Update attachment"', response.content)
        self.client.force_login(user=self.user)
        response = self.client.get(update_url_for_obj(self.attachment))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(update_url_for_obj(self.attachment_other_structure))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object_other_structure.get_detail_url()}")

    def test_post_update_url(self):
        self.client.force_login(user=self.superuser)
        response = self.client.post(update_url_for_obj(self.attachment),
                                    data=self.attachmentPostData(),
                                    )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object.get_detail_url()}?tab=attachments")
        self.attachment.refresh_from_db()
        self.assertEqual(self.attachment.legend, "A legend")
        self.client.force_login(user=self.user)
        response = self.client.get(update_url_for_obj(self.attachment))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(update_url_for_obj(self.attachment_other_structure))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object_other_structure.get_detail_url()}")


class UploadDeleteAttachmentTestCase(SetUpTestDataMixin, TestCase):

    def test_get_delete_with_perms_url(self):
        self.user = SuperUserFactory.create()
        self.client.force_login(user=self.superuser)
        response = self.client.get(delete_url_for_obj(self.attachment))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object.get_detail_url()}?tab=attachments")
        self.assertEqual(1, AccessibilityAttachment.objects.count())

        self.client.force_login(user=self.user)
        response = self.client.get(update_url_for_obj(self.attachment_other_structure))
        self.assertEqual(response.status_code, 200)

    @mock.patch('django.contrib.auth.models.PermissionsMixin.has_perm')
    def test_get_delete_without_perms_url(self, mocke):
        def user_perms(p, obj=None):
            return {'common.delete_attachment_others': False}.get(p, True)
        self.user = UserFactory()
        mocke.side_effect = user_perms
        self.client.force_login(user=self.user)
        response = self.client.get(delete_url_for_obj(self.attachment))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f"{self.object.get_detail_url()}?tab=attachments")
        self.assertEqual(2, AccessibilityAttachment.objects.count())
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


class ReduceSaveSettingsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = SuperUserFactory(username='bar')
        cls.object = TrekFactory.create(name="foo object")

        file = BytesIO()
        file.name = 'foo_file.txt'
        file.seek(0)
        cls.pk = cls.object.pk

    def get_big_dummy_uploaded_image(self):
        file = BytesIO()
        image = Image.new('RGBA', size=(2000, 4000), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test_big.png'
        file.seek(0)
        return SimpleUploadedFile(file.name, file.read(), content_type='image/png')

    @override_settings(PAPERCLIP_MAX_BYTES_SIZE_IMAGE=1093)
    def test_attachment_is_larger_max_size(self):
        self.client.force_login(self.superuser)

        file = BytesIO()
        image = Image.new('RGBA', size=(200, 400), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'small.png'
        file.seek(0)
        response = self.client.post(
            add_url_for_obj(self.object),
            data={
                'creator': self.superuser,
                'title': "A title",
                'legend': "A legend",
                'attachment_accessibility_file': SimpleUploadedFile(file.name, file.read(), content_type='image/png'),
                'author': "newauthor",
                'info_accessibility': 'slope',
                'next': f"{self.object.get_detail_url()}?tab=attachments"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AccessibilityAttachment.objects.count(), 1)

        big_image = self.get_big_dummy_uploaded_image()
        response = self.client.post(
            add_url_for_obj(self.object),
            data={
                'creator': self.superuser,
                'title': "A title",
                'legend': "A legend",
                'attachment_accessibility_file': big_image,
                'author': "newauthor",
                'info_accessibility': 'slope',
                'next': f"{self.object.get_detail_url()}?tab=attachments"
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccessibilityAttachment.objects.count(), 1)
        self.assertIn(b'The uploaded file is too large', response.content)

    @override_settings(PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH=50)
    def test_attachment_is_not_wide_enough(self):
        self.client.force_login(self.superuser)

        file = BytesIO()
        image = Image.new('RGBA', size=(51, 400), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'big.png'
        file.seek(0)
        response = self.client.post(
            add_url_for_obj(self.object),
            data={
                'creator': self.superuser,
                'title': "A title",
                'attachment_accessibility_file': SimpleUploadedFile(file.name, file.read(), content_type='image/png'),
                'author': "newauthor",
                'legend': "A legend",
                'info_accessibility': 'slope',
                'next': f"{self.object.get_detail_url()}?tab=attachments"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AccessibilityAttachment.objects.count(), 1)

        small_file = BytesIO()
        small_image = Image.new('RGBA', size=(49, 400), color=(155, 0, 0))
        small_image.save(small_file, 'png')
        small_file.name = 'small.png'
        small_file.seek(0)
        response = self.client.post(
            add_url_for_obj(self.object),
            data={
                'creator': self.superuser,
                'title': "A title",
                'legend': "A legend",
                'attachment_accessibility_file': SimpleUploadedFile(small_file.name, small_file.read(), content_type='image/png'),
                'author': "newauthor",
                'info_accessibility': 'slope',
                'next': f"{self.object.get_detail_url()}?tab=attachments"
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccessibilityAttachment.objects.count(), 1)
        self.assertIn(b'The uploaded file is not wide enough', response.content)

    @override_settings(PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT=50)
    def test_attachment_is_not_tall_enough(self):
        # Create attachment with small image
        self.client.force_login(self.superuser)

        file = BytesIO()
        image = Image.new('RGBA', size=(400, 51), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'big.png'
        file.seek(0)
        response = self.client.post(
            add_url_for_obj(self.object),
            data={
                'creator': self.superuser,
                'title': "A title",
                'legend': "A legend",
                'attachment_accessibility_file': SimpleUploadedFile(file.name, file.read(), content_type='image/png'),
                'author': "newauthor",
                'info_accessibility': 'slope',
                'next': f"{self.object.get_detail_url()}?tab=attachments"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AccessibilityAttachment.objects.count(), 1)

        small_file = BytesIO()
        small_image = Image.new('RGBA', size=(400, 49), color=(155, 0, 0))
        small_image.save(small_file, 'png')
        small_file.name = 'small.png'
        small_file.seek(0)
        response = self.client.post(
            add_url_for_obj(self.object),
            data={
                'creator': self.superuser,
                'title': "A title",
                'attachment_accessibility_file': SimpleUploadedFile(small_file.name, small_file.read(), content_type='image/png'),
                'author': "newauthor",
                'legend': "A legend",
                'info_accessibility': 'slope',
                'next': f"{self.object.get_detail_url()}?tab=attachments"
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccessibilityAttachment.objects.count(), 1)
        self.assertIn(b'The uploaded file is not tall enough', response.content)

    def test_attachment_deleted(self):
        # Create attachment with small image
        self.client.force_login(self.superuser)
        attachment = AttachmentAccessibilityFactory.create(content_object=self.object)
        os.remove(attachment.attachment_accessibility_file.path)
        response = self.client.post(
            update_url_for_obj(attachment),
            data={
                'creator': self.superuser,
                'title': "A title",
                'attachment_accessibility_file': get_dummy_uploaded_image("title.png"),
                'author': "newauthor",
                'legend': "A legend",
                'info_accessibility': 'slope',
                'next': f"{self.object.get_detail_url()}?tab=attachments"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AccessibilityAttachment.objects.count(), 1)
