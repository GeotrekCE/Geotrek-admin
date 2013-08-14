import os

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from mapentity.tests import MapEntityTest

from geotrek.settings import EnvIniReader
from .factories import AttachmentFactory
from .utils import almostequal, smart_urljoin, sampling


class CommonTest(MapEntityTest):
    def test_attachment(self):
        if self.model is None:
            return  # Abstract test should not run
        obj = self.modelfactory.create()
        AttachmentFactory.create(obj=obj)
        AttachmentFactory.create(obj=obj)
        self.assertEqual(len(obj.attachments), 2)


class ViewsTest(TestCase):
    def test_settings_json(self):
        url = reverse('common:settings_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class UtilsTest(TestCase):
    def test_almostequal(self):
        self.assertTrue(almostequal(0.001, 0.002))
        self.assertFalse(almostequal(0.001, 0.002, precision=3))
        self.assertFalse(almostequal(1, 2, precision=0))
        self.assertFalse(almostequal(-1, 1))
        self.assertFalse(almostequal(1, -1))

    def test_smart_urljoin(self):
        self.assertEqual('http://server.com/foo/path-12.ext',
                         smart_urljoin('http://server.com', '/foo/path-12.ext'))
        self.assertEqual('http://server.com/foo/path-12.ext',
                         smart_urljoin('http://server.com/foo', 'path-12.ext'))
        self.assertEqual('http://server.com/foo/bar/path-12.ext',
                         smart_urljoin('http://server.com/foo', '/bar/path-12.ext'))
        self.assertEqual('http://server.com/foo/bar/path-12.ext',
                         smart_urljoin('http://server.com/foo', 'bar/path-12.ext'))
        self.assertEqual('http://server.com/foo/bar/path-12.ext',
                         smart_urljoin('http://server.com/foo/', '/bar/path-12.ext'))

    def test_sampling(self):
        self.assertEqual([0, 2, 4, 6, 8], sampling(range(10), 5))
        self.assertEqual([0, 3, 6, 9], sampling(range(10), 3))
        self.assertEqual(['a', 'd', 'g', 'j'], sampling('abcdefghijkl', 4))


class EnvIniTests(TestCase):
    ini_file = os.path.join(settings.TEMP_DIR, 'conf.ini')

    def setUp(self):
        with open(self.ini_file, 'w') as f:
            f.write("""[settings]\nkey = value\nkeyint = 3""")
        self.envini = EnvIniReader(self.ini_file)
        os.environ['KEYINT'] = '4'

    def test_existing_key(self):
        self.assertEqual(self.envini.get('key'), 'value')
        self.assertEqual(self.envini.get('keyint'), '4')
        self.assertEqual(self.envini.get('keyint', env=False), '3')

    def test_missing_key(self):
        self.assertEqual(self.envini.get('unknown', 'void'), 'void')
        self.assertEqual(self.envini.get('unknown', None), None)
        self.assertRaises(ImproperlyConfigured, self.envini.get, 'unknown')

    def tearDown(self):
        os.remove(self.ini_file)
