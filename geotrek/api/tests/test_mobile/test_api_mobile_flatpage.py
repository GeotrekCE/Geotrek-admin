from django.urls import reverse
from django.test.testcases import TestCase
from django.utils import translation
from geotrek.common.tests.factories import TargetPortalFactory

from geotrek.flatpages.tests.factories import FlatPageFactory, MenuItemFactory
from geotrek.flatpages.models import FlatPage, FLATPAGES_TARGETS

FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'title', 'external_url', 'content'
])


class FlatPageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        translation.activate('fr')
        cls.flatpage = FlatPageFactory.create(published_fr=True)
        cls.menu_item = MenuItemFactory.create(page=cls.flatpage)
        flatpage2 = FlatPageFactory.create(published_fr=True)
        MenuItemFactory.create(page=flatpage2)

    def get_flatpage_list(self, params=None):
        return self.client.get(reverse('apimobile:flatpage-list'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_flatpage_detail(self, id_flatpage, params=None):
        return self.client.get(reverse('apimobile:flatpage-detail', args=(id_flatpage,)),
                               params, HTTP_ACCEPT_LANGUAGE='fr')

    def test_flatpage_list(self):
        response = self.get_flatpage_list()
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0].get('title'), FlatPage.objects.first().title)

    def test_flatpage_detail(self):
        response = self.get_flatpage_detail(self.flatpage.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE)
        self.assertEqual(json_response.get('content'), self.flatpage.content)
        self.assertEqual(json_response.get('title'), self.flatpage.title)

    def test_flatpage_detail_with_lang_param(self):
        fp = FlatPageFactory(published_en=True, published_fr=True, title_fr="Bonjour", title_en="Hello")

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=(fp.pk, )),
            HTTP_ACCEPT_LANGUAGE='fr')

        self.assertEqual(resp.status_code, 200)
        title = resp.json()["title"]
        self.assertEqual(title, "Bonjour")

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=(fp.pk,)),
            HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(resp.status_code, 200)
        title = resp.json()["title"]
        self.assertEqual(title, "Hello")

    def test_flatpage_detail_with_lang_param(self):
        fp = FlatPageFactory(published_en=True, published_fr=True, title_fr="Bonjour", title_en="Hello")
        fp2 = FlatPageFactory(published_en=True, published_fr=True, title_fr="Au revoir", title_en="Goodbye")

        resp = self.client.get(reverse('apimobile:flatpage-list'), HTTP_ACCEPT_LANGUAGE='fr')

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        self.assertEqual(len(results), 4)
        self.assertEqual(results[2]["title"], "Bonjour")
        self.assertEqual(results[3]["title"], "Au revoir")

        resp = self.client.get(reverse('apimobile:flatpage-list'), HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Hello")
        self.assertEqual(results[1]["title"], "Goodbye")

    def test_flatpage_list_published_only_with_lang_param(self):
        FlatPage.objects.update(published_en=False, published_fr=False)

        FlatPageFactory(published_en=False, published_fr=False)
        fp1 = FlatPageFactory(published_en=True, published_fr=False)
        fp2 = FlatPageFactory(published_en=False, published_fr=True)
        fp3 = FlatPageFactory(published_en=True, published_fr=True)

        resp = self.client.get(reverse('apimobile:flatpage-list'), HTTP_ACCEPT_LANGUAGE='fr')

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        self.assertEqual(len(results), 2)
        fp_ids = [r["id"] for r in results]
        self.assertIn(fp2.id, fp_ids)
        self.assertIn(fp3.id, fp_ids)

        resp = self.client.get(reverse('apimobile:flatpage-list'), HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        self.assertEqual(len(results), 2)
        fp_ids = [r["id"] for r in results]
        self.assertIn(fp1.id, fp_ids)
        self.assertIn(fp3.id, fp_ids)

    def test_flatpage_detail_published_only_with_lang_param(self):
        fp1 = FlatPageFactory(published_en=True, published_fr=False)
        fp2 = FlatPageFactory(published_en=False, published_fr=True)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=(fp1.pk, )),
            HTTP_ACCEPT_LANGUAGE='fr')

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=(fp2.pk,)),
            HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(resp.status_code, 404)

    def test_flatpage_detail_with_portal_filter(self):
        p1 = TargetPortalFactory()
        p2 = TargetPortalFactory()
        fp0 = FlatPageFactory(published_fr=True, portals=None)
        fp1 = FlatPageFactory(published_fr=True, portals=[p1])
        fp2 = FlatPageFactory(published_fr=True, portals=[p2])
        fp3 = FlatPageFactory(published_fr=True, portals=[p1, p2])

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=[fp0.pk]),
            data={"portal": p2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], fp0.id)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=[fp1.pk]),
            data = {"portal": p2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=[fp2.pk]),
            data={"portal": p2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], fp2.id)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=[fp3.pk]),
            data={"portal": p2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], fp3.id)

    def test_flatpage_list_with_portal_filter(self):
        FlatPage.objects.update(published_fr=False)
        p1 = TargetPortalFactory()
        p2 = TargetPortalFactory()
        fp0 = FlatPageFactory(published_fr=True, portals=None)
        fp1 = FlatPageFactory(published_fr=True, portals=[p1])
        fp2 = FlatPageFactory(published_fr=True, portals=[p2])
        fp3 = FlatPageFactory(published_fr=True, portals=[p1, p2])

        resp = self.client.get(
            reverse('apimobile:flatpage-list'),
            data={"portal": p2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        page_ids = [r["id"] for r in results]
        self.assertEqual(len(page_ids), 3)
        self.assertIn(fp0.id, page_ids)
        self.assertIn(fp2.id, page_ids)
        self.assertIn(fp3.id, page_ids)

    def test_flatpage_list_returns_ordered_pages(self):
        FlatPage.objects.update(published_fr=False)
        fp0 = FlatPageFactory(published_fr=True, order=2)
        fp1 = FlatPageFactory(published_fr=True, order=3)
        fp2 = FlatPageFactory(published_fr=True, order=1)

        resp = self.client.get(
            reverse('apimobile:flatpage-list'),
            HTTP_ACCEPT_LANGUAGE='fr'
        )

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        page_ids = [r["id"] for r in results]
        self.assertEqual(page_ids, [fp2.id, fp0.id, fp1.id])

    def test_flatpage_list_filter_by_target(self):
        FlatPage.objects.update(published_fr=False)
        fp0 = FlatPageFactory(published_fr=True, target=FLATPAGES_TARGETS.HIDDEN)
        fp1 = FlatPageFactory(published_fr=True, target=FLATPAGES_TARGETS.MOBILE)
        fp2 = FlatPageFactory(published_fr=True, target=FLATPAGES_TARGETS.ALL)
        fp3 = FlatPageFactory(published_fr=True, target=FLATPAGES_TARGETS.WEB)

        resp = self.client.get(
            reverse('apimobile:flatpage-list'),
            HTTP_ACCEPT_LANGUAGE='fr'
        )

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        page_ids = [r["id"] for r in results]
        self.assertEqual(len(page_ids), 2)
        self.assertIn(fp1.id, page_ids)
        self.assertIn(fp2.id, page_ids)

    def tearDown(self):
        translation.deactivate()
