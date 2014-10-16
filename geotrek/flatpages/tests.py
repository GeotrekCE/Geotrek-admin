from django.test import TestCase
from django.core.exceptions import ValidationError

from mapentity.factories import SuperUserFactory
from geotrek.flatpages.factories import FlatPageFactory


class FlatPageModelTest(TestCase):
    def test_slug_is_taken_from_title(self):
        fp = FlatPageFactory(title="C'est pour toi")
        self.assertEquals(fp.slug, 'cest-pour-toi')

    def test_target_is_all_by_default(self):
        fp = FlatPageFactory()
        self.assertEquals(fp.target, 'all')

    def test_publication_date_is_filled_if_published(self):
        fp = FlatPageFactory()
        fp.save()
        self.assertIsNone(fp.publication_date)
        fp.published = True
        fp.save()
        self.assertIsNotNone(fp.publication_date)

    def test_validation_fails_if_both_url_and_content_are_filled(self):
        fp = FlatPageFactory(external_url="http://geotrek.fr",
                             content="<p>Boom!</p>")
        self.assertRaises(ValidationError, fp.clean)

    def test_validation_does_not_fail_if_url_and_content_are_falsy(self):
        fp = FlatPageFactory(external_url="  ",
                             content="<p></p>")
        fp.clean()


class AdminSiteTest(TestCase):
    def login(self):
        user = SuperUserFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def test_flatpages_are_registered(self):
        self.login()
        response = self.client.get('/admin/flatpages/flatpage/')
        self.assertEquals(response.status_code, 200)

    def test_flatpages_are_translatable(self):
        self.login()
        response = self.client.get('/admin/flatpages/flatpage/add/')
        self.assertContains(response, 'published_en')
