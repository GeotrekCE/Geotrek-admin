from django.test import TestCase
from geotrek.authent.factories import UserFactory


class ProfileViewsTest(TestCase):
    def test_profile_model_do_not_exist(self):
        user = UserFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)
        response = self.client.get('/media/profiles/infrastructuretype-1.png')
        self.assertEqual(response.status_code, 404)
