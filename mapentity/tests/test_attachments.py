from unittest import mock
from django.core.management import call_command

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from paperclip.settings import get_attachment_model, get_filetype_model
from mapentity.views.generic import MapEntityDetail

from geotrek.tourism.models import TouristicEvent
from geotrek.tourism.factories import TouristicEventFactory


def add_url_for_obj(obj):
    return reverse('add_attachment', kwargs={
        'app_label': obj._meta.app_label,
        'model_name': obj._meta.model_name,
        'pk': obj.pk
    })


class EntityAttachmentTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('howard', 'h@w.com', 'booh')

        def user_perms(p):
            return {'paperclip.add_attachment': False}.get(p, True)
        self.user.has_perm = mock.MagicMock(side_effect=user_perms)
        self.object = TouristicEventFactory.create()
        call_command('update_geotrek_permissions', verbosity=0)

    def createRequest(self):
        request = RequestFactory().get('/dummy')
        request.session = {}
        request.user = self.user
        return request

    def createAttachment(self, obj):
        uploaded = SimpleUploadedFile('file.odt',
                                      b'*' * 128,
                                      content_type='application/vnd.oasis.opendocument.text')
        kwargs = {
            'content_type': ContentType.objects.get_for_model(obj),
            'object_id': obj.pk,
            'filetype': get_filetype_model().objects.create(),
            'creator': self.user,
            'title': "Attachment title",
            'legend': "Attachment legend",
            'attachment_file': uploaded
        }
        return get_attachment_model().objects.create(**kwargs)

    def test_list_attachments_in_details(self):
        self.createAttachment(self.object)
        self.user.user_permissions.add(Permission.objects.get(codename='read_touristicevent'))
        self.user.user_permissions.add(Permission.objects.get(codename='read_attachment'))
        self.client.login(username='howard', password='booh')
        response = self.client.get('/touristicevent/{pk}/'.format(pk=self.object.pk))

        html = response.content
        self.assertTemplateUsed(response, template_name='paperclip/attachment_list.html')

        self.assertEqual(1, len(get_attachment_model().objects.attachments_for_object(self.object)))

        self.assertNotIn(b"Submit attachment", html)

        for attachment in get_attachment_model().objects.attachments_for_object(self.object):
            self.assertIn(attachment.legend.encode(), html)
            self.assertIn(attachment.title.encode(), html)
            self.assertIn(attachment.attachment_file.url.encode(), html)
            self.assertIn(b'paperclip/fileicons/odt.png', html)

    def test_upload_form_in_details_if_perms(self):
        self.user.has_perm = mock.MagicMock(return_value=True)
        view = MapEntityDetail.as_view(model=TouristicEvent,
                                       template_name="mapentity/mapentity_detail.html")
        request = self.createRequest()
        response = view(request, pk=self.object.pk)
        html = response.render()
        self.assertIn(b"Submit attachment", html.content)
        self.assertIn(
            '<form  action="/paperclip/add-for/tourism/touristicevent/{}/'.format(self.object.pk).encode(), html.content)


class UploadAttachmentTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.object = TouristicEventFactory.create()
        user = User.objects.create_user('aah', 'email@corp.com', 'booh')
        user.is_superuser = True
        user.save()
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def attachmentPostData(self):
        filetype = get_filetype_model().objects.create()
        uploaded = SimpleUploadedFile('face.jpg',
                                      b'*' * 128,
                                      content_type='image/jpeg')
        data = {
            'filetype': filetype.pk,
            'title': 'A title',
            'legend': 'A legend',
            'attachment_file': uploaded,
            'attachment_video': '',
            'embed': 'False',
            'next': self.object.get_detail_url()
        }
        return data

    def test_upload_redirects_to_dummy_detail_url(self):
        response = self.client.post(add_url_for_obj(self.object),
                                    data=self.attachmentPostData())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'],
                         '/touristicevent/%s/' % self.object.pk)

    def test_upload_creates_attachment(self):
        data = self.attachmentPostData()
        self.client.post(add_url_for_obj(self.object), data=data)
        att = get_attachment_model().objects.attachments_for_object(self.object).get()
        self.assertEqual(att.title, data['title'])
        self.assertEqual(att.legend, data['legend'])
        self.assertEqual(att.filetype.pk, data['filetype'])

    def test_title_gives_name_to_file(self):
        data = self.attachmentPostData()
        self.client.post(add_url_for_obj(self.object), data=data)
        att = get_attachment_model().objects.attachments_for_object(self.object).get()
        self.assertTrue('a-title' in att.attachment_file.name)

    def test_filename_is_used_if_no_title(self):
        data = self.attachmentPostData()
        data['title'] = ''
        self.client.post(add_url_for_obj(self.object), data=data)
        att = get_attachment_model().objects.attachments_for_object(self.object).get()
        self.assertTrue('face' in att.attachment_file.name)
