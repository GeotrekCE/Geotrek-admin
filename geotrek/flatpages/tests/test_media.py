from django.test import TestCase

from geotrek.flatpages.tests.factories import FlatPageFactory


class FlatPageMediaTest(TestCase):
    def test_media_is_empty_if_content_is_none(self):
        page = FlatPageFactory()
        self.assertEqual(page.parse_media(), [])

    def test_media_is_empty_if_content_has_no_image(self):
        page = FlatPageFactory(content="""<h1>One page</h1><body>One looove</body>""")
        self.assertEqual(page.parse_media(), [])

    def test_media_returns_all_images_attributes(self):
        html = """
        <h1>One page</h1>
        <body><p>Yéâh</p>
        <img src="/media/image1.png" title="Image 1" alt="image-1"/>
        <img src="/media/image2.jpg"/>
        <img title="No src"/>
        </body>
        """
        page = FlatPageFactory(content=html)
        self.assertEqual(page.parse_media(), [
            {'url': '/media/image1.png', 'title': 'Image 1', 'alt': 'image-1', 'mimetype': ['image', 'png']},
            {'url': '/media/image2.jpg', 'title': '', 'alt': '', 'mimetype': ['image', 'jpeg']}
        ])
