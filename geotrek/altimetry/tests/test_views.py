from django.contrib.gis.geos import LineString
from django.db import connection
from django.test import TestCase

from geotrek import settings
from geotrek.authent.tests.factories import UserFactory
from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.tests.factories import TrekFactory


class ProfileViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_profile_model_do_not_exist(self):
        self.client.force_login(user=self.user)
        response = self.client.get('/media/profiles/infrastructuretype-1.png')
        self.assertEqual(response.status_code, 404)

    def test_profile_object_not_public_not_connected(self):
        trek = TrekFactory.create(name='Trek', published=False)
        response = self.client.get('/media/profiles/trek-%s.png' % trek.pk)
        self.assertEqual(response.status_code, 403)

    def test_profile_object_not_public_connected(self):
        self.client.force_login(user=self.user)
        trek = TrekFactory.create(name='Trek', published=False)
        response = self.client.get('/media/profiles/trek-%s.png' % trek.pk)
        self.assertEqual(response.status_code, 403)

    def test_profile_object_public_fail_no_profile(self):
        self.client.force_login(user=self.user)
        trek = TrekFactory.create(name='Trek', published=True)
        response = self.client.get('/media/profiles/trek-%s.png' % trek.pk)
        self.assertEqual(response.status_code, 200)


class ProfileCacheTests(TestCase):
    """ Test profile svg is cached """
    @classmethod
    def setUpTestData(cls):
        # Create a simple fake DEM
        with connection.cursor() as cur:
            cur.execute('INSERT INTO altimetry_dem (rast) VALUES (ST_MakeEmptyRaster(100, 125, 0, 125, 25, -25, 0, 0, %s))', [settings.SRID])
            cur.execute('UPDATE altimetry_dem SET rast = ST_AddBand(rast, \'16BSI\')')
            demvalues = [[0, 0, 3, 5], [2, 2, 10, 15], [5, 15, 20, 25], [20, 25, 30, 35], [30, 35, 40, 45]]
            for y in range(0, 5):
                for x in range(0, 4):
                    cur.execute('UPDATE altimetry_dem SET rast = ST_SetValue(rast, %s, %s, %s::float)', [x + 1, y + 1, demvalues[y][x]])
        cls.path = PathFactory.create(geom=LineString((1, 101), (81, 101), (81, 99)))
        cls.trek = TrekFactory.create(paths=[cls.path])

    def test_cache_is_used_when_getting_trek_profile(self):
        # There are 6 queries to get trek profile
        with self.assertNumQueries(6):
            response = self.client.get(f"/api/fr/treks/{self.trek.pk}/profile.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        # When cache is used there are only 2 queries to get trek profile
        with self.assertNumQueries(2):
            response = self.client.get(f"/api/fr/treks/{self.trek.pk}/profile.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_cache_is_used_when_getting_trek_profile_svg(self):
        # There are 6 queries to get trek profile svg
        with self.assertNumQueries(6):
            response = self.client.get(f"/api/fr/treks/{self.trek.pk}/profile.svg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/svg+xml')
        # When cache is used there are only 5 queries to get trek profile
        with self.assertNumQueries(5):
            response = self.client.get(f"/api/fr/treks/{self.trek.pk}/profile.svg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/svg+xml')
