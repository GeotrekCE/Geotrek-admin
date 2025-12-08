import base64

import factory
from django.core.files.uploadedfile import SimpleUploadedFile

# Produce a small red dot
IMG_FILE = b"iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="

SVG_FILE = (
    b'<svg width="3cm" height="2cm" version="1.1"> '
    b'<title> Rectangle </title> <desc> Un rectangle </desc> <rect x="0.5cm" y="0.5cm" width="2cm" height="1cm"/></svg>'
)


def get_dummy_img():
    return base64.b64decode(IMG_FILE)


def get_dummy_uploaded_image(name="dummy_img.png"):
    return SimpleUploadedFile(name, get_dummy_img(), content_type="image/png")


def get_dummy_uploaded_image_svg(name="dummy_img.svg"):
    return SimpleUploadedFile(name, SVG_FILE, content_type="image/svg+xml")


def get_dummy_uploaded_file(name="dummy_file.txt"):
    return SimpleUploadedFile(name, b"HelloWorld", content_type="text/plain")


def get_dummy_uploaded_document(name="dummy_file.odt", size=128):
    return SimpleUploadedFile(
        name, b"*" * size, content_type="application/vnd.oasis.opendocument.text"
    )


def dummy_filefield_as_sequence(toformat_name):
    """Simple helper method to fill a models.FileField"""
    return factory.Sequence(lambda n: get_dummy_uploaded_image(toformat_name % n))
