from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from geotrek.authent.tests.factories import UserProfileFactory
from geotrek.common.models import FileType, Attachment
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.flatpages.models import FlatPage

from geotrek.flatpages.tests.factories import FlatPageFactory
from mapentity.tests.factories import SuperUserFactory


class AdminSiteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_flatpages_are_registered(self):
        response = self.client.get('/admin/flatpages/flatpage/')
        self.assertEqual(response.status_code, 200)

    def test_flatpages_are_translatable(self):
        response = self.client.get('/admin/flatpages/flatpage/add/')
        self.assertContains(response, 'published_en')

    def test_flatpages_are_updatable(self):
        page = FlatPageFactory(content="One looove")
        response = self.client.get('/admin/flatpages/flatpage/{0}/change/'.format(page.pk))
        self.assertContains(response, "One looove")


class FlatPageAdminFormViewsTestCase(TestCase):
    def setUp(self) -> None:
        profile = UserProfileFactory(
            user__username='spammer',
            user__password='pipo'
        )
        user = profile.user

        user.is_staff = True
        user.save()
        add_perm = Permission.objects.get(codename="add_flatpage")
        view_perm = Permission.objects.get(codename="view_flatpage")
        update_perm = Permission.objects.get(codename="change_flatpage")
        delete_perm = Permission.objects.get(codename="delete_flatpage")
        user.user_permissions.add(add_perm, view_perm, update_perm, delete_perm)

        success = self.client.login(username=user.username, password='pipo')
        self.assertTrue(success)
        self.user = user

    def test_save_without_cover_image(self):
        data = {
            'title_en': 'Title',
            'external_url_en': 'http://geotrek.fr',
            'target': 'all',
        }

        url = reverse('admin:flatpages_flatpage_add')
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FlatPage.objects.count(), 1)
        page = FlatPage.objects.get()
        self.assertEqual(page.title, 'Title')
        self.assertEqual(page.external_url, 'http://geotrek.fr')
        self.assertEqual(page.target, 'all')

    def test_save_with_cover_image(self):
        data = {
            'title_en': 'Title',
            'external_url_en': 'http://geotrek.fr',
            'target': 'all',
            'cover_image_author': 'Someone',
            'cover_image': get_dummy_uploaded_image("flatpage_cover.png"),
        }

        url = reverse('admin:flatpages_flatpage_add')
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FlatPage.objects.count(), 1)
        page = FlatPage.objects.get()
        attachment = Attachment.objects.get()
        self.assertEqual(attachment.content_object, page)
        self.assertEqual(attachment.author, 'Someone')

    def test_save_delete_cover_image(self):
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
            creator=self.user
        )
        data = {
            'title_en': 'Title',
            'external_url_en': 'http://geotrek.fr',
            'target': 'all',
            'cover_image_author': '',
            'cover_image-clear': 'on',
        }

        url = reverse('admin:flatpages_flatpage_change', args=[page.pk])
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Attachment.objects.exists())
