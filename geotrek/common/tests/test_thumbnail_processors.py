from django.test import TestCase
from PIL import Image

from geotrek.common.thumbnail_processors import add_watermark


class AddWatermarkTest(TestCase):
    def test_add_watermark_with_text_and_size(self):
        image = Image.new("RGB", (60, 30), color="red")
        kwargs = {"TEXT": "Test", "SIZE_WATERMARK": 10}
        result = add_watermark(image, **kwargs)
        self.assertIsInstance(result, Image.Image)

    def test_add_watermark_without_text(self):
        image = Image.new("RGB", (60, 30), color="red")
        kwargs = {"TEXT": "", "SIZE_WATERMARK": 10}
        result = add_watermark(image, **kwargs)
        self.assertEqual(result, image)

    def test_add_watermark_with_text_and_without_size(self):
        image = Image.new("RGB", (60, 30), color="red")
        kwargs = {"TEXT": "Test", "SIZE_WATERMARK": None}
        with self.assertRaises(TypeError):
            add_watermark(image, **kwargs)

    def test_add_watermark_with_size_and_without_text(self):
        image = Image.new("RGB", (60, 30), color="red")
        kwargs = {"TEXT": None, "SIZE_WATERMARK": 10}
        result = add_watermark(image, **kwargs)
        self.assertEqual(result, image)

    def test_add_watermark_without_text_and_size(self):
        image = Image.new("RGB", (60, 30), color="red")
        kwargs = {"TEXT": None, "SIZE_WATERMARK": None}
        result = add_watermark(image, **kwargs)
        self.assertEqual(result, image)
