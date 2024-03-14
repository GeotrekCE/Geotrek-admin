from django.urls import reverse
from django.test.testcases import TestCase
from django.utils import translation
from geotrek.common.tests.factories import TargetPortalFactory

from geotrek.flatpages.tests.factories import FlatPageFactory
from geotrek.flatpages.models import FlatPage, FLATPAGES_TARGETS

FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'title', 'external_url', 'content'
])


class FlatPageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        translation.activate('fr')
        cls.flatpage = FlatPageFactory.create(published_fr=True)
        FlatPageFactory.create(published_fr=True)

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
        page = FlatPageFactory(published_en=True, published_fr=True, title_fr="Bonjour", title_en="Hello")

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=(page.pk, )),
            HTTP_ACCEPT_LANGUAGE='fr')

        self.assertEqual(resp.status_code, 200)
        title = resp.json()["title"]
        self.assertEqual(title, "Bonjour")

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=(page.pk,)),
            HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(resp.status_code, 200)
        title = resp.json()["title"]
        self.assertEqual(title, "Hello")

    def test_flatpage_list_with_lang_param(self):
        FlatPageFactory(published_en=True, published_fr=True, title_fr="Bonjour", title_en="Hello")
        FlatPageFactory(published_en=True, published_fr=True, title_fr="Au revoir", title_en="Goodbye")

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
        page1 = FlatPageFactory(published_en=True, published_fr=False)
        page2 = FlatPageFactory(published_en=False, published_fr=True)
        page3 = FlatPageFactory(published_en=True, published_fr=True)

        resp = self.client.get(reverse('apimobile:flatpage-list'), HTTP_ACCEPT_LANGUAGE='fr')

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        self.assertEqual(len(results), 2)
        page_ids = [r["id"] for r in results]
        self.assertIn(page2.id, page_ids)
        self.assertIn(page3.id, page_ids)

        resp = self.client.get(reverse('apimobile:flatpage-list'), HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        self.assertEqual(len(results), 2)
        page_ids = [r["id"] for r in results]
        self.assertIn(page1.id, page_ids)
        self.assertIn(page3.id, page_ids)

    def test_flatpage_detail_published_only_with_lang_param(self):
        page1 = FlatPageFactory(published_en=True, published_fr=False)
        page2 = FlatPageFactory(published_en=False, published_fr=True)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=(page1.pk, )),
            HTTP_ACCEPT_LANGUAGE='fr')

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=(page2.pk,)),
            HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(resp.status_code, 404)

    def test_flatpage_detail_with_portal_filter(self):
        portal1 = TargetPortalFactory()
        portal2 = TargetPortalFactory()
        page1 = FlatPageFactory(published_fr=True, portals=None)
        page2 = FlatPageFactory(published_fr=True, portals=[portal1])
        page3 = FlatPageFactory(published_fr=True, portals=[portal2])
        page4 = FlatPageFactory(published_fr=True, portals=[portal1, portal2])

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=[page1.pk]),
            data={"portal": portal2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], page1.id)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=[page2.pk]),
            data={"portal": portal2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=[page3.pk]),
            data={"portal": portal2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], page3.id)

        resp = self.client.get(
            reverse('apimobile:flatpage-detail', args=[page4.pk]),
            data={"portal": portal2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], page4.id)

    def test_flatpage_list_with_portal_filter(self):
        FlatPage.objects.update(published_fr=False)
        portal1 = TargetPortalFactory()
        portal2 = TargetPortalFactory()
        page1 = FlatPageFactory(published_fr=True, portals=None)
        FlatPageFactory(published_fr=True, portals=[portal1])
        page2 = FlatPageFactory(published_fr=True, portals=[portal2])
        page3 = FlatPageFactory(published_fr=True, portals=[portal1, portal2])

        resp = self.client.get(
            reverse('apimobile:flatpage-list'),
            data={"portal": portal2.name},
            HTTP_ACCEPT_LANGUAGE='fr'
        )

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        page_ids = [r["id"] for r in results]
        self.assertEqual(len(page_ids), 3)
        self.assertIn(page1.id, page_ids)
        self.assertIn(page2.id, page_ids)
        self.assertIn(page3.id, page_ids)

    def test_flatpage_list_returns_ordered_pages(self):
        FlatPage.objects.update(published_fr=False)
        page1 = FlatPageFactory(published_fr=True, order=2)
        page2 = FlatPageFactory(published_fr=True, order=3)
        page3 = FlatPageFactory(published_fr=True, order=1)

        resp = self.client.get(
            reverse('apimobile:flatpage-list'),
            HTTP_ACCEPT_LANGUAGE='fr'
        )

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        page_ids = [r["id"] for r in results]
        self.assertEqual(page_ids, [page3.id, page1.id, page2.id])

    def test_flatpage_list_filter_by_target(self):
        FlatPage.objects.update(published_fr=False)
        FlatPageFactory(published_fr=True, target=FLATPAGES_TARGETS.HIDDEN)
        page1 = FlatPageFactory(published_fr=True, target=FLATPAGES_TARGETS.MOBILE)
        page2 = FlatPageFactory(published_fr=True, target=FLATPAGES_TARGETS.ALL)
        FlatPageFactory(published_fr=True, target=FLATPAGES_TARGETS.WEB)

        resp = self.client.get(
            reverse('apimobile:flatpage-list'),
            HTTP_ACCEPT_LANGUAGE='fr'
        )

        self.assertEqual(resp.status_code, 200)
        results = resp.json()
        page_ids = [r["id"] for r in results]
        self.assertEqual(len(page_ids), 2)
        self.assertIn(page1.id, page_ids)
        self.assertIn(page2.id, page_ids)

    def tearDown(self):
        translation.deactivate()
