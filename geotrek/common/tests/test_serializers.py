import io
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.exceptions import ValidationError

from geotrek.common.serializers import (
    AttachmentSerializer,
    HDViewPointGeoJSONSerializer,
)
from geotrek.trekking.tests.factories import TrekFactory

from .factories import HDViewPointFactory


class HDViewPointSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trek = TrekFactory()
        cls.vp = HDViewPointFactory(content_object=cls.trek)

    def test_geojson_serializer(self):
        serializer = HDViewPointGeoJSONSerializer(instance=self.vp)
        coords = serializer.data.get("geometry").get("coordinates")
        geom_transformed = self.vp.geom.transform(4326, clone=True)
        self.assertAlmostEqual(coords[0], geom_transformed.x)
        self.assertAlmostEqual(coords[1], geom_transformed.y)


def make_image_bytes(width=800, height=600, image_format="JPEG"):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color="red").save(buffer, format=image_format)
    buffer.seek(0)
    return buffer.read()


@override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="en", LANGUAGE_CODE="en")
class AttachmentSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.serializer = AttachmentSerializer()

        content = make_image_bytes(800, 600, "JPEG")
        cls.valid_image_file = SimpleUploadedFile(
            "photo.jpg", content, content_type="image/jpeg"
        )

    def test_valid_image_passes(self):
        file = self.valid_image_file
        result = self.serializer.validate_attachment_file(file)
        self.assertIs(result, file)

    @override_settings(PAPERCLIP_ALLOWED_EXTENSIONS=None)
    def test_non_image_file_passes(self):
        content = b"%PDF-1.4 fake pdf content, not a real image"
        file = SimpleUploadedFile("doc.pdf", content, content_type="application/pdf")
        result = self.serializer.validate_attachment_file(file)
        self.assertIs(result, file)

    @override_settings(PAPERCLIP_MAX_BYTES_SIZE_IMAGE=10)
    def test_file_too_large_raises(self):
        file = self.valid_image_file
        with self.assertRaisesMessage(
            ValidationError, "The uploaded file is too large"
        ):
            self.serializer.validate_attachment_file(file)

    @override_settings(PAPERCLIP_ALLOWED_EXTENSIONS=["png"])
    def test_extension_not_allowed(self):
        file = self.valid_image_file
        with self.assertRaisesMessage(ValidationError, "File type 'jpg' not allowed"):
            self.serializer.validate_attachment_file(file)

    @override_settings(PAPERCLIP_ALLOWED_EXTENSIONS=["jpg"])
    def test_mimetype_mismatch_raises(self):
        content = make_image_bytes(image_format="PNG")
        file = SimpleUploadedFile("photo.jpg", content, content_type="image/jpeg")
        with self.assertRaisesMessage(
            ValidationError, "File mime type 'image/png' is not allowed for jpg."
        ):
            self.serializer.validate_attachment_file(file)

    @override_settings(
        PAPERCLIP_ALLOWED_EXTENSIONS=None, PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH=2000
    )
    def test_image_not_wide_enough(self):
        file = self.valid_image_file
        with self.assertRaisesMessage(
            ValidationError, "The uploaded file is not wide enough"
        ):
            self.serializer.validate_attachment_file(file)

    @override_settings(
        PAPERCLIP_ALLOWED_EXTENSIONS=None, PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT=2000
    )
    def test_image_not_tall_enough(self):
        file = self.valid_image_file
        with self.assertRaisesMessage(
            ValidationError, "The uploaded file is not tall enough"
        ):
            self.serializer.validate_attachment_file(file)

    @override_settings(PAPERCLIP_ALLOWED_EXTENSIONS=None)
    @patch("geotrek.common.serializers.Image.open")
    def test_decompression_bomb_raises(self, mock_magic):
        mock_magic.side_effect = ValueError("Decompressed Data Too Large")
        file = self.valid_image_file
        with self.assertRaisesMessage(ValidationError, "Decompressed Data Too Large"):
            self.serializer.validate_attachment_file(file)
