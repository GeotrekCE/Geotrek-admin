from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import TrekkingManagerFactory


class TrekkingManagerTest(AuthentFixturesTest):
    def login(self):
        self.user = TrekkingManagerFactory(password='booh')
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)
