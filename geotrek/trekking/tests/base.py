from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import TrekkingManagerFactory


class TrekkingManagerTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = TrekkingManagerFactory(password='booh')

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)
