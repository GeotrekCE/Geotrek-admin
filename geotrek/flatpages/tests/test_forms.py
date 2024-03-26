from django.test import TestCase

from geotrek.authent.tests.factories import UserProfileFactory
from geotrek.flatpages.forms import FlatPageForm


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
