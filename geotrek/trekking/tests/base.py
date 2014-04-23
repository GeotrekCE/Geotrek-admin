from geotrek.authent.tests import AuthentFixturesTest
from geotrek.authent.factories import TrekkingManagerFactory


class TrekkingManagerTest(AuthentFixturesTest):
    def login(self):
        user = TrekkingManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)
