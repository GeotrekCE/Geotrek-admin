from django.urls import reverse

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import PathManagerFactory

from .factories import StakeFactory


class StakeAdminTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = PathManagerFactory.create()
        cls.stake = StakeFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_stake_can_be_deleted(self):
        delete_url = reverse("admin:core_stake_delete", args=[self.stake.pk])
        detail_url = reverse("admin:core_stake_change", args=[self.stake.pk])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(delete_url, {"post": "yes"})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/")
