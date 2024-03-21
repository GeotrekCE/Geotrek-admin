from django.test import TestCase
from embed_video.backends import UnknownIdException, detect_backend

from geotrek.common.embed.backends import DailymotionBackend


class DailymotionBackendTestCase(TestCase):
    urls = (
        ("https://www.dailymotion.com/video/x8uw0jq", "x8uw0jq"),
        ("http://www.dailymotion.com/video/x8uw0jq", "x8uw0jq"),
        ("https://dailymotion.com/video/x8uw0jq", "x8uw0jq"),
        ("http://dailymotion.com/video/x8uw0jq", "x8uw0jq"),
        ("https://dai.ly/x8uw09k", "x8uw09k"),
        ("http://dai.ly/x8uw09k", "x8uw09k"),
    )

    instance = DailymotionBackend

    def test_detect(self):
        for url in self.urls:
            backend = detect_backend(url[0])
            self.assertIsInstance(backend, self.instance)

    def test_code(self):
        for url in self.urls:
            backend = self.instance(url[0])
            self.assertEqual(backend.code, url[1])

    def test_youtube_keyerror(self):
        """Test for issue #7"""
        backend = self.instance("https://www.toto.com/watch?id=5")
        self.assertRaises(UnknownIdException, backend.get_code)

    def test_thumbnail(self):
        for url in self.urls:
            backend = self.instance(url[0])
            self.assertIn(url[1], backend.thumbnail)
