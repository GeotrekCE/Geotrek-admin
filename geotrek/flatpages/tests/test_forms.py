from django.test import TestCase

from geotrek.authent.factories import UserProfileFactory
from geotrek.common.models import Attachment, FileType
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.flatpages.forms import FlatPageForm
from geotrek.flatpages.models import FlatPage


class FlatPageFormTest(TestCase):
    def login(self):
        profile = UserProfileFactory(
            user__username='spammer',
            user__password='pipo'
        )
        user = profile.user
        success = self.client.login(username=user.username, password='pipo')
        self.assertTrue(success)
        return user

    def test_validation_does_not_fail_if_content_is_none_and_url_is_filled(self):
        user = self.login()
        data = {
            'title_en': 'Reduce your flat page',
            'external_url_en': 'http://geotrek.fr',
            'target': 'all',
        }
        form = FlatPageForm(data=data, user=user)
        self.assertTrue(form.is_valid())

    def test_validation_does_fail_if_url_is_badly_filled(self):
        user = self.login()
        data = {
            'title_fr': 'Reduce your flat page',
            'external_url_fr': 'pipo-pipo-pipo-pipo',
            'target': 'all',
        }
        form = FlatPageForm(data=data, user=user)
        self.assertFalse(form.is_valid())

    def test_save_without_cover(self):
        user = self.login()
        data = {
            'title_en': 'Title',
            'external_url_en': 'http://geotrek.fr',
            'target': 'all',
        }
        form = FlatPageForm(data, user=user)
        self.assertTrue(form.is_valid())
        form.save()
        page = FlatPage.objects.get()
        self.assertEqual(page.title, 'Title')
        self.assertEqual(page.external_url, 'http://geotrek.fr')
        self.assertEqual(page.target, 'all')

    def test_save_with_cover(self):
        user = self.login()
        data = {
            'title_en': 'Title',
            'external_url_en': 'http://geotrek.fr',
            'target': 'all',
            'cover_image_author': 'Someone',
        }
        file_data = {
            'cover_image': get_dummy_uploaded_image(),
        }
        form = FlatPageForm(data, file_data, user=user)
        self.assertTrue(form.is_valid())
        form.save()
        page = FlatPage.objects.get()
        attachment = Attachment.objects.get()
        self.assertEqual(attachment.content_object, page)
        self.assertEqual(attachment.author, 'Someone')

    def test_save_delete_cover(self):
        user = self.login()
        page = FlatPage.objects.create(
            title='Title',
            external_url='http://geotrek.fr',
            target='all'
        )
        filetype = FileType.objects.create(type="Photographie")
        Attachment.objects.create(
            content_object=page,
            attachment_file=get_dummy_uploaded_image(),
            author='Someone',
            filetype=filetype,
            creator=user
        )
        data = {
            'title_en': 'Title',
            'external_url_en': 'http://geotrek.fr',
            'target': 'all',
            'cover_image_author': '',
            'cover_image-clear': 'on',
        }
        form = FlatPageForm(data, instance=page, user=user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertFalse(Attachment.objects.exists())
