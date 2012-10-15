from django.test import TestCase
from django.core.urlresolvers import reverse

from .utils import almostequal, smart_urljoin


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
