from mapentity.tests import SuperUserFactory

from django.test import TestCase
from django.urls import reverse

from geotrek.authent.tests.factories import UserProfileFactory
from geotrek.common.models import Attachment, FileType
from geotrek.common.utils.testdata import get_dummy_uploaded_image
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

    # def test_validation_does_not_fail_if_content_is_none_and_url_is_filled(self):
    #     user = self.login()
    #     data = {
    #         'title_en': 'Reduce your flat page',
    #         'external_url_en': 'http://geotrek.fr',
    #         'target': 'all',
    #     }
    #     form = FlatPageForm(data=data, user=user)
    #     self.assertTrue(form.is_valid())

    # def test_validation_does_fail_if_url_is_badly_filled(self):
    #     user = self.login()
    #     data = {
    #         'title_fr': 'Reduce your flat page',
    #         'external_url_fr': 'pipo-pipo-pipo-pipo',
    #         'target': 'all',
    #     }
    #     form = FlatPageForm(data=data, user=user)
    #     self.assertFalse(form.is_valid())

    def test_save_without_cover(self):
        # user = self.login()
        # TODO: use a regular user with permissions instead of a superuser
        superuser = SuperUserFactory()
        self.client.force_login(superuser)

        data = {
            "title_en": "Hello English World!",
            "_position": "first-child",
        }
        url = reverse('admin:flatpages_flatpage_add')
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FlatPage.objects.count(), 1)
        page = FlatPage.objects.get()
        self.assertEqual(page.title, 'Hello English World!')

    def test_save_with_cover(self):
        # user = self.login()
        # TODO: use a regular user with permissions instead of a superuser
        superuser = SuperUserFactory()
        self.client.force_login(superuser)

        with get_dummy_uploaded_image().open() as image_file:
            data = {
                "title_en": "Hello World!",
                "_position": "first-child",
                "cover_image": image_file,
                'cover_image_author': 'Someone',
            }
            url = reverse('admin:flatpages_flatpage_add')
            response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FlatPage.objects.count(), 1)
        page = FlatPage.objects.get()
        self.assertEqual(Attachment.objects.count(), 1)
        attachment = Attachment.objects.get()
        self.assertEqual(attachment.content_object, page)
        self.assertEqual(attachment.author, 'Someone')

    def test_save_delete_cover(self):
        superuser = SuperUserFactory.create()
        # user = self.login()
        # TODO: use a regular user with permissions instead of a superuser
        page = FlatPage(
            title='Title',
        )
        FlatPage.add_root(instance=page)
        page.save()
        filetype = FileType.objects.create(type="Photographie")
        Attachment.objects.create(
            content_object=page,
            attachment_file=get_dummy_uploaded_image(),
            author='Someone',
            filetype=filetype,
            creator=superuser
        )

        url = reverse('admin:flatpages_flatpage_change', args=[page.pk])
        self.client.force_login(superuser)
        response = self.client.post(url, data={
            "title_en": "Hello World!",
            "_position": "first-child",
            'cover_image-clear': 'on',
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Attachment.objects.exists())
