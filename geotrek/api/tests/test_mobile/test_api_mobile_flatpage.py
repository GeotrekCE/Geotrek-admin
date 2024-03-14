from django.conf import settings
from django.urls import reverse
from django.test.testcases import TestCase
from django.utils import translation
from geotrek.common.tests.factories import TargetPortalFactory

from geotrek.flatpages.tests.factories import FlatPageFactory, MenuItemFactory
from geotrek.flatpages.models import FlatPage, FLATPAGES_TARGETS

FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'title', 'external_url', 'content'
])


def _create_flatpage_and_menuitem(**kwargs):
    """Support function to convert all FlatPages created for the tests into
    a couple FlatPage + MenuItem. The mobile API stays the same (only a "virtual" FlatPage type is exposed) but
    there are now 2 models under the hood.
    """

    # Those fields are copied from FlatPage to MenuItem
    # keys are FlatPage's fieldnames, values are MenuItem's
    copied_fields = {
        "title": "label",
        "published": "published",
        "portals": "portals",
    }

    # Same principle: those fields are moved from FlatPage to MenuItem
    moved_fields = {
        "external_url": "link_url",
        "target": "platform",
    }

    # Those fields are removed from FlatPage
    removed_fields = [
        "order",
    ]

    # Those fields are translated so we copy/move all translation values
    translated_fields = [
        "title",
        "published",
        "external_url",
    ]

    page_kwargs = kwargs.copy()
    for field in list(moved_fields.keys()) + removed_fields:
        try:
            del page_kwargs[field]
        except KeyError:
            pass
    page = FlatPageFactory.create(**page_kwargs)

    if kwargs.get("target") == "hidden":
        return page

    menu_kwargs = {}
    menu_fields = {}
    menu_fields.update(copied_fields)
    menu_fields.update(moved_fields)
    for src, dst in menu_fields.items():
        if src in translated_fields:
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                try:
                    menu_kwargs[f"{dst}_{lang}"] = kwargs[f"{src}_{lang}"]
                except KeyError:
                    pass
        else:
            try:
                menu_kwargs[dst] = kwargs[src]
            except KeyError:
                pass
    MenuItemFactory.create(page=page, **menu_kwargs)

    return page


class FlatPageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        translation.activate('fr')
        cls.flatpage = _create_flatpage_and_menuitem(published_fr=True)
        _create_flatpage_and_menuitem(published_fr=True)

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
        page = _create_flatpage_and_menuitem(published_en=True, published_fr=True, title_fr="Bonjour", title_en="Hello")

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
        _create_flatpage_and_menuitem(published_en=True, published_fr=True, title_fr="Bonjour", title_en="Hello")
        _create_flatpage_and_menuitem(published_en=True, published_fr=True, title_fr="Au revoir", title_en="Goodbye")

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

        _create_flatpage_and_menuitem(published_en=False, published_fr=False)
        page1 = _create_flatpage_and_menuitem(published_en=True, published_fr=False)
        page2 = _create_flatpage_and_menuitem(published_en=False, published_fr=True)
        page3 = _create_flatpage_and_menuitem(published_en=True, published_fr=True)

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
        page1 = _create_flatpage_and_menuitem(published_en=True, published_fr=False)
        page2 = _create_flatpage_and_menuitem(published_en=False, published_fr=True)

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
        page1 = _create_flatpage_and_menuitem(published_fr=True, portals=None)
        page2 = _create_flatpage_and_menuitem(published_fr=True, portals=[portal1])
        page3 = _create_flatpage_and_menuitem(published_fr=True, portals=[portal2])
        page4 = _create_flatpage_and_menuitem(published_fr=True, portals=[portal1, portal2])

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
        page1 = _create_flatpage_and_menuitem(published_fr=True, portals=None)
        _create_flatpage_and_menuitem(published_fr=True, portals=[portal1])
        page2 = _create_flatpage_and_menuitem(published_fr=True, portals=[portal2])
        page3 = _create_flatpage_and_menuitem(published_fr=True, portals=[portal1, portal2])

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

        # I cannot use the _create_flatpage_and_menuitem for this test because it is
        # the order of creation of MenuItems which defines their position/order,
        # and I also want to diffentiate the order of MenuItems from the order by FlatPages pk.
        page1 = FlatPageFactory(published_fr=True)
        page2 = FlatPageFactory(published_fr=True)
        page3 = FlatPageFactory(published_fr=True)
        MenuItemFactory(published_fr=True, page=page3)
        MenuItemFactory(published_fr=True, page=page1)
        MenuItemFactory(published_fr=True, page=page2)

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
        _create_flatpage_and_menuitem(published_fr=True, target=str(FLATPAGES_TARGETS.HIDDEN))
        page1 = _create_flatpage_and_menuitem(published_fr=True, target=str(FLATPAGES_TARGETS.MOBILE))
        page2 = _create_flatpage_and_menuitem(published_fr=True, target=str(FLATPAGES_TARGETS.ALL))
        _create_flatpage_and_menuitem(published_fr=True, target=str(FLATPAGES_TARGETS.WEB))

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
