import os
import requests
from unittest import mock

from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos.error import GEOSException
from django.http import HttpResponse
from django.test import TestCase

from mapentity.registry import app_settings
from mapentity.helpers import (
    capture_url,
    capture_map_image,
    convertit_url,
    user_has_perm,
    download_to_stream,
    bbox_split_srid_2154,
    api_bbox,
    wkt_to_geom,
    is_file_uptodate
)
import shutil


class GeomHelpersTest(TestCase):
    def setUp(self):
        self.bbox = (200000, 300000, 1100000, 1200000)

    def test_bbox_split_srid_2154_cycle(self):
        bbox = bbox_split_srid_2154(self.bbox, by_x=2, by_y=2, cycle=True)
        polygon_1 = Polygon.from_bbox(next(bbox))
        polygon_2 = Polygon.from_bbox(next(bbox))
        polygon_3 = Polygon.from_bbox(next(bbox))
        polygon_4 = Polygon.from_bbox(next(bbox))
        self.assertEqual(polygon_1,
                         "POLYGON ((200000 300000, 200000 750000, 650000 750000, 650000 300000, 200000 300000))")
        self.assertEqual(polygon_2,
                         "POLYGON ((200000 750000, 200000 1200000, 650000 1200000, 650000 750000, 200000 750000))")
        self.assertEqual(polygon_3,
                         "POLYGON ((650000 300000, 650000 750000, 1100000 750000, 1100000 300000, 650000 300000))")
        self.assertEqual(polygon_4,
                         "POLYGON ((650000 750000, 650000 1200000, 1100000 1200000, 1100000 750000, 650000 750000))")
        polygon_5 = Polygon.from_bbox(next(bbox))
        self.assertEqual(polygon_1, polygon_5)

    def test_bbox_split_srid_2154_no_cycle(self):
        bbox = bbox_split_srid_2154(self.bbox, by_x=2, by_y=2, cycle=False)
        polygon_1 = Polygon.from_bbox(next(bbox))
        polygon_2 = Polygon.from_bbox(next(bbox))
        polygon_3 = Polygon.from_bbox(next(bbox))
        polygon_4 = Polygon.from_bbox(next(bbox))
        self.assertEqual(polygon_1,
                         "POLYGON ((200000 300000, 200000 750000, 650000 750000, 650000 300000, 200000 300000))")
        self.assertEqual(polygon_2,
                         "POLYGON ((200000 750000, 200000 1200000, 650000 1200000, 650000 750000, 200000 750000))")
        self.assertEqual(polygon_3,
                         "POLYGON ((650000 300000, 650000 750000, 1100000 750000, 1100000 300000, 650000 300000))")
        self.assertEqual(polygon_4,
                         "POLYGON ((650000 750000, 650000 1200000, 1100000 1200000, 1100000 750000, 650000 750000))")
        with self.assertRaises(StopIteration):
            Polygon.from_bbox(next(bbox))

    def test_api_bbox(self):
        bbox = api_bbox(self.bbox, srid=2154, buffer=0.5)
        self.assertAlmostEqual(bbox[0], -3.54172018720)
        self.assertAlmostEqual(bbox[1], -7.12818833979)
        self.assertAlmostEqual(bbox[2], 8.85446791766)
        self.assertAlmostEqual(bbox[3], 5.09712579633)
        bbox_no_buffer = api_bbox(self.bbox, srid=2154, buffer=0.0)
        self.assertAlmostEqual(bbox_no_buffer[0], -0.44426741142)
        self.assertAlmostEqual(bbox_no_buffer[1], -4.02805866362)
        self.assertAlmostEqual(bbox_no_buffer[2], 5.75604304925)
        self.assertAlmostEqual(bbox_no_buffer[3], 1.99700039676)

    def test_wkt_to_geom(self):
        geom_wkt = "POINT (650000 750000)"
        geom = wkt_to_geom(geom_wkt, srid_from=2154)
        self.assertEqual(geom.ewkt, "SRID=2154;%s" % geom_wkt)

    def test_wkt_to_geom_fail(self):
        geom_wkt = "GeometryCollection2 (1090 1090)"
        with self.assertRaises(GEOSException):
            wkt_to_geom(geom_wkt)


class OtherHelpers(TestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(os.path.join('tmp')):
            os.makedirs(os.path.join('tmp'))

    def setUp(self):
        self.path = os.path.join('tmp', 'test.txt')

    @mock.patch("os.path.exists", return_value=True)
    def test_is_file_uptodate_no_date(self, mock_value):
        self.assertFalse(is_file_uptodate(self.path, None))

    @mock.patch('requests.get')
    def test_download_to_stream_source_is_None(self, mock_get):
        def itfails(url, headers):
            raise requests.exceptions.ConnectionError()
        mock_get.side_effect = itfails
        source = download_to_stream('fake_url', 'fake_stream', silent=True)
        self.assertIsNone(source)

    @mock.patch('requests.get')
    @mock.patch('django.http.HttpResponse.write', side_effect=IOError("Test"))
    def test_download_to_stream_source_error_io(self, mock_write, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        with self.assertRaises(IOError):
            download_to_stream('fake_url', HttpResponse('test', content_type='text/javascript'))

    @mock.patch('requests.get')
    def test_download_to_stream_source_header(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        mock_get.return_value.headers = {'data': 'test'}
        response = HttpResponse('test', content_type='text/javascript')
        download_to_stream('fake_url', response)
        self.assertEqual(response['data'], 'test')

    @mock.patch('requests.get')
    def test_capture_map_image_no_size(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        capture_map_image('fake_url', 'tmp/test.txt')
        self.assertTrue(os.path.exists(os.path.join('tmp', 'test.txt')))
        os.remove(os.path.join('tmp', 'test.txt'))

    @mock.patch('requests.get')
    def test_capture_map_image_aspect(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        capture_map_image('fake_url', 'tmp/test.txt', aspect=0.1)
        self.assertTrue(os.path.exists(os.path.join('tmp', 'test.txt')))
        os.remove(os.path.join('tmp', 'test.txt'))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(os.path.join('tmp'))


class MapEntityCaptureHelpersTest(TestCase):
    def test_capture_url_uses_setting(self):
        orig = app_settings['CAPTURE_SERVER']
        app_settings['CAPTURE_SERVER'] = 'https://vlan'
        url = capture_url('')
        self.assertTrue(url.startswith('https://vlan'))
        app_settings['CAPTURE_SERVER'] = orig

    def test_capture_url_is_escaped(self):
        url = capture_url('http://geotrek.fr')
        self.assertIn('http%3A//geotrek.fr', url)

    def test_capture_url_with_no_params(self):
        url = capture_url('http://geotrek.fr')
        self.assertNotIn('width', url)
        self.assertNotIn('height', url)
        self.assertNotIn('selector', url)

    def test_capture_url_with_width_params(self):
        url = capture_url('http://geotrek.fr', width=800)
        self.assertIn('width=800', url)

    def test_capture_url_with_selector_params(self):
        url = capture_url('http://geotrek.fr', selector="#bazinga")
        self.assertIn('%23bazinga', url)


class MapEntityConvertHelpersTest(TestCase):

    def test_convert_url_uses_setting(self):
        orig = app_settings['CONVERSION_SERVER']
        app_settings['CONVERSION_SERVER'] = 'https://vlan'
        url = convertit_url('')
        self.assertTrue(url.startswith('https://vlan'))
        app_settings['CONVERSION_SERVER'] = orig

    def test_convert_url_is_escaped(self):
        url = convertit_url('http://geotrek.fr')
        self.assertIn('http%3A//geotrek.fr', url)

    def test_convert_url_default_is_pdf(self):
        url = convertit_url('')
        self.assertIn('to=application/pdf', url)
        url = convertit_url('', to_type=None)
        self.assertIn('to=application/pdf', url)

    def test_convert_url_default_no_from(self):
        url = convertit_url('')
        self.assertNotIn('from=', url)

    def test_convert_url_format_extension_becomes_mimetype(self):
        url = convertit_url('', to_type="doc")
        self.assertIn('to=application/msword', url)

    def test_convert_url_from_is_escaped(self):
        url = convertit_url('', from_type="application/#bb")
        self.assertIn('from=application/%23bb', url)


class UserHasPermTest(TestCase):
    def setUp(self):
        self.user = mock.MagicMock()

    def test_return_true_if_anonymous_has_perm(self):
        orig = app_settings['ANONYMOUS_VIEWS_PERMS']
        app_settings['ANONYMOUS_VIEWS_PERMS'] = ('view-perm',)
        self.assertTrue(user_has_perm(self.user, 'view-perm'))
        app_settings['ANONYMOUS_VIEWS_PERMS'] = orig


class DownloadStreamTest(TestCase):

    @mock.patch('mapentity.helpers.requests.get')
    def test_headers_can_be_specified_for_download(self, get_mocked):
        # Required to specified language for example
        get_mocked.return_value.status_code = 200
        get_mocked.return_value.content = "x"
        download_to_stream('http://google.com', open(os.devnull, 'w'), silent=True, headers={'Accept-language': 'fr'})
        get_mocked.assert_called_with('http://google.com', headers={'Accept-language': 'fr'})
