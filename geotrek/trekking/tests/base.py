from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import TrekkingManagerFactory


class TrekkingManagerTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = TrekkingManagerFactory(password="booh")

    def login(self):
        self.client.force_login(user=self.user)
