# -*- coding: utf-8 -*-
import os
import json
from django.core import management
from django.conf import settings
from django.test import TestCase
from mapentity.factories import SuperUserFactory
from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory
from geotrek.flatpages.factories import FlatPageFactory
from geotrek.authent.factories import UserProfileFactory
from geotrek.flatpages.forms import FlatPageForm
from geotrek.flatpages.models import FlatPage


class FlatPageFormTest(TestCase):
    def login(self):
        profile = UserProfileFactory(
            user__username='spammer',
            user__password='pipo'
        )
        user = profile.user
        success = self.client.login(username=user.username, password='pipo')
        self.assertTrue(success)
        return user

    def test_validation_does_not_fail_if_content_is_none_and_url_is_filled(self):
        user = self.login()
        data = {
            'title_fr': 'Reduce your flat page',
            'external_url_fr': 'http://geotrek.fr',
            'target': 'all',
        }
        form = FlatPageForm(data=data, user=user)
        self.assertTrue(form.is_valid())

    def test_validation_does_fail_if_url_is_badly_filled(self):
        user = self.login()
        data = {
            'title_fr': 'Reduce your flat page',
            'external_url_fr': 'pipo-pipo-pipo-pipo',
            'target': 'all',
        }
        form = FlatPageForm(data=data, user=user)
        self.assertFalse(form.is_valid())


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

    def test_validation_does_not_fail_if_url_and_content_are_falsy(self):
        fp = FlatPageFactory(external_url="  ",
                             content="<p></p>")
        fp.clean()

    def test_validation_does_not_fail_if_url_is_none(self):
        fp = FlatPageFactory(external_url=None,
                             content="<p></p>")
        fp.clean()

    def test_retrieve_by_order(self):
        try:
            fp = FlatPageFactory.create_batch(5)
            for index, flatpage in enumerate(FlatPage.objects.all()):
                if index == 0:
                    continue
                self.assertGreater(flatpage.order, int(fp[index - 1].order))
        finally:
            for f in fp:
                f.clean()

    def test_retrieve_by_id_if_order_is_the_same(self):
        try:
            fp = FlatPageFactory.create_batch(5, order=0)
            for index, flatpage in enumerate(FlatPage.objects.all()):
                if index == 0:
                    continue
                self.assertGreater(flatpage.id, fp[index - 1].id)
        finally:
            for f in fp:
                f.clean()


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

    def test_flatpages_are_updatable(self):
        self.login()
        page = FlatPageFactory(content="One looove")
        response = self.client.get('/admin/flatpages/flatpage/{0}/'.format(page.pk))
        self.assertContains(response, "One looove")


class RESTViewsTest(TestCase):
    def setUp(self):
        FlatPageFactory.create_batch(10, published=True)
        FlatPageFactory.create(published=False)

    def test_records_list(self):
        response = self.client.get('/api/en/flatpages.json')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.content)
        self.assertEquals(len(records), 10)

    def test_serialized_attributes(self):
        response = self.client.get('/api/en/flatpages.json')
        records = json.loads(response.content)
        record = records[0]
        self.assertEquals(
            sorted(record.keys()),
            sorted([u'content', u'external_url', u'id', u'last_modified',
                    u'media', u'portal', u'publication_date', u'published',
                    u'published_status', u'slug', u'source', u'target',
                    u'title']))


class SyncTestPortal(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncTestPortal, cls).setUpClass()
        cls.source_a = RecordSourceFactory()
        cls.source_b = RecordSourceFactory()
        cls.portal_a = TargetPortalFactory()
        cls.portal_b = TargetPortalFactory()

        FlatPageFactory.create(published=True,
                               sources=(cls.source_a,))
        FlatPageFactory.create(portals=(cls.portal_a, cls.portal_b),
                               published=True)
        FlatPageFactory.create(published=True,
                               sources=(cls.source_b,))
        FlatPageFactory.create(portals=(cls.portal_a,),
                               published=True)

    def test_sync(self):
        '''
        Test synced flatpages
        '''
        management.call_command('sync_rando', settings.SYNC_RANDO_ROOT, url='http://localhost:8000',
                                skip_tiles=True, verbosity='0')
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', lang, 'flatpages.geojson'), 'r') as f:
                flatpages = json.load(f)
                self.assertEquals(len(flatpages),
                                  FlatPage.objects.filter(**{'published_{}'.format(lang): True}).count())

    def test_sync_filtering_sources(self):
        '''
        Test if synced flatpages are filtered by source
        '''
        management.call_command('sync_rando', settings.SYNC_RANDO_ROOT, url='http://localhost:8000',
                                source=self.source_a.name, skip_tiles=True, verbosity='0')
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', lang, 'flatpages.geojson'), 'r') as f:
                flatpages = json.load(f)
                self.assertEquals(len(flatpages),
                                  FlatPage.objects.filter(source__name__in=[self.source_a.name, ],
                                                          **{'published_{}'.format(lang): True}).count())

    def test_sync_filtering_portal(self):
        '''
        Test if synced flatpages are filtered by portal
        '''
        management.call_command('sync_rando', settings.SYNC_RANDO_ROOT, url='http://localhost:8000',
                                portal=self.portal_a.name, skip_tiles=True, verbosity='0')
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', lang, 'flatpages.geojson'), 'r') as f_file:
                flatpages = json.load(f_file)
                self.assertEquals(len(flatpages),
                                  FlatPage.objects.filter(portal__name__in=[self.portal_a.name, ],
                                                          **{'published_{}'.format(lang): True}).count())
