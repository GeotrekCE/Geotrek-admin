from django.urls import reverse

from geotrek.authent.tests import AuthentFixturesTest
from geotrek.authent.tests.factories import PathManagerFactory

from .factories import StakeFactory


class StakeAdminTest(AuthentFixturesTest):
    def setUp(self):
        self.user = PathManagerFactory.create(password='booh')
        self.stake = StakeFactory.create()

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def test_stake_can_be_deleted(self):
        self.login()
        delete_url = reverse('admin:core_stake_delete', args=[self.stake.pk])
        detail_url = reverse('admin:core_stake_change', args=[self.stake.pk])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(delete_url, {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/')
