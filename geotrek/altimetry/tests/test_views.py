from django.test import TestCase
from django.contrib.gis.geos import LineString
from django.core.urlresolvers import NoReverseMatch

from geotrek.authent.factories import UserFactory
from geotrek.trekking.factories import TrekFactory


class ProfileViewsTest(TestCase):
    def setUp(self):
        self.user = UserFactory(password='booh')

    def test_profile_model_do_not_exist(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)
        response = self.client.get('/media/profiles/infrastructuretype-1.png')
        self.assertEqual(response.status_code, 404)

    def test_profile_object_not_public_not_connected(self):
        trek = TrekFactory.create(name='POI', no_path=True, published=False)
        response = self.client.get('/media/profiles/trek-%s.png' % trek.pk)
        self.assertEqual(response.status_code, 403)

    def test_profile_object_not_public_connected(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)
        trek = TrekFactory.create(name='POI', no_path=True, published=False)
        response = self.client.get('/media/profiles/trek-%s.png' % trek.pk)
        self.assertEqual(response.status_code, 403)

    def test_profile_object_public_fail_no_profile(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)
        trek = TrekFactory.create(name='POI', no_path=True, published=True)
        response = self.client.get('/media/profiles/trek-%s.png' % trek.pk)
        self.assertEqual(response.status_code, 200)
