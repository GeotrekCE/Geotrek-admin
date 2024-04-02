from tempfile import TemporaryDirectory

from django.test import TestCase
from django.urls import reverse
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from mapentity.tests import SuperUserFactory


class TinyMCEUploadViewTestCase(TestCase):

    def test_tinymce_upload(self):
        user = SuperUserFactory()
        self.client.force_login(user)
        file = get_dummy_uploaded_image("tinymce_uploaded_image.png")

        with TemporaryDirectory() as tmp_dir:
            with self.settings(MEDIA_ROOT=tmp_dir):
                url = reverse("flatpages:tinymce_upload")
                response = self.client.post(url, data={"file": file})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("location", data)
        location = data["location"]
        self.assertTrue(location.startswith("http://") or location.startswith("https://"))
        self.assertIn("tinymce_uploaded_image", location)
