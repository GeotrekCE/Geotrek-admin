# -*- coding: utf8 -*-
import json

from django.test import TestCase
from django.core.exceptions import ValidationError

from mapentity.factories import SuperUserFactory
from geotrek.flatpages.factories import FlatPageFactory


class FlatPageModelTest(TestCase):
    def test_slug_is_taken_from_title(self):
        fp = FlatPageFactory(title="C'est pour toi")
        self.assertEquals(fp.slug, 'cest-pour-toi')

    def test_target_is_all_by_default(self):
        fp = FlatPageFactory()
        self.assertEquals(fp.target, 'all')

    def test_publication_date_is_filled_if_published(self):
        fp = FlatPageFactory()
        fp.save()
        self.assertIsNone(fp.publication_date)
        fp.published = True
        fp.save()
        self.assertIsNotNone(fp.publication_date)

    def test_validation_fails_if_both_url_and_content_are_filled(self):
        fp = FlatPageFactory(external_url="http://geotrek.fr",
                             content="<p>Boom!</p>")
        self.assertRaises(ValidationError, fp.clean)

    def test_validation_fails_if_both_url_and_content_are_in_any_language(self):
        fp = FlatPageFactory(external_url="http://geotrek.fr",
                             content_it="<p>Boom!</p>")
        self.assertRaises(ValidationError, fp.clean)

    def test_validation_does_not_fail_if_url_and_content_are_falsy(self):
        fp = FlatPageFactory(external_url="  ",
                             content="<p></p>")
        fp.clean()


class FlatPageMediaTest(TestCase):
    def test_media_is_empty_if_content_is_none(self):
        page = FlatPageFactory()
        self.assertEqual(page.parse_media(), [])

    def test_media_is_empty_if_content_has_no_image(self):
        page = FlatPageFactory(content="""<h1>One page</h1><body>One looove</body>""")
        self.assertEqual(page.parse_media(), [])

    def test_media_returns_all_images_attributes(self):
        html = u"""
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


class AdminSiteTest(TestCase):
    def login(self):
        user = SuperUserFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def test_flatpages_are_registered(self):
        self.login()
        response = self.client.get('/admin/flatpages/flatpage/')
        self.assertEquals(response.status_code, 200)

    def test_flatpages_are_translatable(self):
        self.login()
        response = self.client.get('/admin/flatpages/flatpage/add/')
        self.assertContains(response, 'published_en')


class RESTViewsTest(TestCase):
    def setUp(self):
        FlatPageFactory.create_batch(10)

    def login(self):
        user = SuperUserFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def test_endpoint_is_protected(self):
        response = self.client.get('/api/flatpages/')
        self.assertEquals(response.status_code, 403)

    def test_records_list(self):
        self.login()
        response = self.client.get('/api/flatpages/')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.content)
        self.assertEquals(len(records), 10)

    def test_serialized_attributes(self):
        self.login()
        response = self.client.get('/api/flatpages/')
        records = json.loads(response.content)
        record = records[0]
        self.assertEquals(sorted(record.keys()),
                          [u'content', u'external_url', u'id', u'last_modified',
                           u'media',
                           u'publication_date', u'published', u'published_status',
                           u'slug', u'target', u'title'])
