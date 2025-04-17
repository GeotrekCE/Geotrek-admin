from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory

from geotrek.common.models import Attachment, FileType
from geotrek.common.tests.factories import TargetPortalFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.flatpages.models import FlatPage, MenuItem
from geotrek.flatpages.tests.factories import FlatPageFactory, MenuItemFactory


def _flatten(fieldsets):
    fields = []
    for fieldset in fieldsets:
        for field in fieldset[1]["fields"]:
            fields.append(field)
    return fields


class AdminSiteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_flatpages_are_registered(self):
        response = self.client.get("/admin/flatpages/flatpage/")
        self.assertEqual(response.status_code, 200)

    def test_flatpages_are_translatable(self):
        response = self.client.get("/admin/flatpages/flatpage/add/")
        self.assertContains(response, "published_en")

    def test_flatpages_are_updatable(self):
        page = FlatPageFactory(content="One looove")
        response = self.client.get(f"/admin/flatpages/flatpage/{page.pk}/change/")
        self.assertContains(response, "One looove")


class FlatPageAdminFormViewsTestCase(TestCase):
    def setUp(self) -> None:
        user = SuperUserFactory()
        self.client.force_login(user)
        self.user = user

    def test_retrieve_list_with_portals_displayed(self):
        portal1 = TargetPortalFactory(name="Portal1")
        portal2 = TargetPortalFactory(name="Portal2")
        FlatPageFactory(title="A flat page with portals", portals=[portal1, portal2])

        url = reverse("admin:flatpages_flatpage_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Portal1, Portal2", response.content)

    def test_retrieve_expected_form_fields(self):
        url = reverse("admin:flatpages_flatpage_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        expected_fields = [
            "title_en",
            "title_fr",
            "title_es",
            "title_it",
            "published_en",
            "published_fr",
            "published_es",
            "published_it",
            "source",
            "portals",
            "cover_image",
            "cover_image_author",
            "content_en",
            "content_fr",
            "content_es",
            "content_it",
            "_position",
            "_ref_node_id",
        ]
        fields = _flatten(response.context["adminform"].fieldsets)
        self.assertEqual(len(fields), len(expected_fields))
        self.assertEqual(set(fields), set(expected_fields))

    def test_save_without_cover_image(self):
        data = {
            "title_en": "Title",
            "_position": "first-child",
        }

        url = reverse("admin:flatpages_flatpage_add")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FlatPage.objects.count(), 1)
        page = FlatPage.objects.get()
        self.assertEqual(page.title, "Title")

    def test_save_with_cover_image(self):
        data = {
            "title_en": "Title",
            "_position": "first-child",
            "cover_image_author": "Someone",
            "cover_image": get_dummy_uploaded_image("flatpage_cover.png"),
        }

        url = reverse("admin:flatpages_flatpage_add")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FlatPage.objects.count(), 1)
        page = FlatPage.objects.get()
        self.assertEqual(Attachment.objects.count(), 1)
        attachment = Attachment.objects.get()
        self.assertEqual(attachment.content_object, page)
        self.assertEqual(attachment.author, "Someone")

    def test_save_delete_cover_image(self):
        page = FlatPage.add_root(title="Title")
        filetype = FileType.objects.create(type="Photographie")
        Attachment.objects.create(
            content_object=page,
            attachment_file=get_dummy_uploaded_image(),
            author="Someone",
            filetype=filetype,
            creator=self.user,
        )

        data = {
            "title_en": "Title",
            "cover_image_author": "",
            "cover_image-clear": "on",
            "_position": "first-child",
        }
        url = reverse("admin:flatpages_flatpage_change", args=[page.pk])
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Attachment.objects.exists())


class MenuItemAdminFormViewsTestCase(TestCase):
    def setUp(self) -> None:
        user = SuperUserFactory()
        self.client.force_login(user)
        self.user = user

    def test_retrieve_list_with_portals_displayed(self):
        portal1 = TargetPortalFactory(name="Portal1")
        portal2 = TargetPortalFactory(name="Portal2")
        MenuItemFactory(title="A menu item with portals", portals=[portal1, portal2])

        url = reverse("admin:flatpages_menuitem_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Portal1, Portal2", response.content)

    def test_retrieve_expected_form_fields(self):
        url = reverse("admin:flatpages_menuitem_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        expected_fields = [
            "title_en",
            "title_fr",
            "title_es",
            "title_it",
            "published_en",
            "published_fr",
            "published_es",
            "published_it",
            "portals",
            "platform",
            "thumbnail",
            "pictogram",
            "target_type",
            "page",
            "link_url_en",
            "link_url_fr",
            "link_url_es",
            "link_url_it",
            "open_in_new_tab",
            "_position",
            "_ref_node_id",
        ]
        fields = _flatten(response.context["adminform"].fieldsets)
        self.assertEqual(len(fields), len(expected_fields))
        self.assertEqual(set(fields), set(expected_fields))

    def test_add(self):
        add_data = {
            "title_en": "Hello World!",
            "platform": "all",
            "_position": "first-child",
        }

        response = self.client.post(
            "/admin/flatpages/menuitem/add/", data=add_data, follow=False
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(MenuItem.objects.filter(title_en="Hello World!").count(), 1)

    def test_udpate(self):
        menu_item = MenuItem.add_root(
            title_en="Already exists",
            platform="web",
        )

        change_data = {
            "title_en": "Already exists and changed",
            "platform": "mobile",
            "_position": "first-child",
        }

        response = self.client.post(
            f"/admin/flatpages/menuitem/{menu_item.id}/change/",
            data=change_data,
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        changed_menu_item = MenuItem.objects.get(pk=menu_item.id)
        self.assertEqual(changed_menu_item.title_en, change_data["title_en"])
        self.assertEqual(changed_menu_item.platform, change_data["platform"])

    def test_save_with_page_is_required_error(self):
        add_data = {
            "title_en": "Hello World!",
            "platform": "all",
            "_position": "first-child",
            "target_type": "page",
            "page": "",
        }

        response = self.client.post(
            "/admin/flatpages/menuitem/add/", data=add_data, follow=False
        )

        self.assertEqual(response.status_code, 200)
        adminform_errors = response.context["adminform"].errors
        self.assertTrue("page" in adminform_errors)
        self.assertTrue("required" in adminform_errors["page"][0])

    def test_save_with_link_url_is_required_error(self):
        link_url_loc_fieldname = (
            "link_url_" + settings.MODELTRANSLATION_DEFAULT_LANGUAGE
        )
        add_data = {
            "title_en": "Hello World!",
            "platform": "all",
            "_position": "first-child",
            "target_type": "link",
            link_url_loc_fieldname: "",
        }

        response = self.client.post(
            "/admin/flatpages/menuitem/add/", data=add_data, follow=False
        )

        self.assertEqual(response.status_code, 200)
        adminform_errors = response.context["adminform"].errors
        self.assertTrue(link_url_loc_fieldname in adminform_errors)
        self.assertTrue("required" in adminform_errors[link_url_loc_fieldname][0])

    def test_retrieve_with_thumbnail(self):
        menu_item = MenuItem.add_root(
            title_en="I have a thumbnail",
        )
        file_type = FileType.objects.create(type="Photographie")
        Attachment.objects.create(
            content_type=ContentType.objects.get_for_model(MenuItem),
            object_id=menu_item.id,
            attachment_file=get_dummy_uploaded_image("menu_item_thumbnail.png"),
            filetype=file_type,
            creator=self.user,
        )

        response = self.client.get(f"/admin/flatpages/menuitem/{menu_item.id}/change/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"menu_item_thumbnail" in response.content)

    def test_save_with_thumbnail(self):
        menu_item = MenuItem.add_root(
            title_en="I have a thumbnail",
        )
        file_type = FileType.objects.create(type="Photographie")
        menu_item_content_type = ContentType.objects.get_for_model(MenuItem)
        Attachment.objects.create(
            content_type=menu_item_content_type,
            object_id=menu_item.id,
            attachment_file=get_dummy_uploaded_image("menu_item_thumbnail.png"),
            filetype=file_type,
            creator=self.user,
        )

        img = get_dummy_uploaded_image("new_thumbnail.png")
        change_data = {
            "title_en": "I have a new thumbnail",
            "platform": "all",
            "_position": "first-child",
            "thumbnail": img,
        }

        response = self.client.post(
            f"/admin/flatpages/menuitem/{menu_item.id}/change/", data=change_data
        )

        self.assertEqual(response.status_code, 302)

        qs = Attachment.objects.filter(
            object_id=menu_item.id, content_type=menu_item_content_type
        ).all()
        self.assertEqual(len(qs), 1)
        thumbnail = qs.first()
        self.assertIn("new_thumbnail", thumbnail.filename)

    def test_save_delete_thumbnail(self):
        menu_item = MenuItem.add_root(
            title_en="I have a thumbnail",
        )
        file_type = FileType.objects.create(type="Photographie")
        menu_item_content_type = ContentType.objects.get_for_model(MenuItem)
        Attachment.objects.create(
            content_type=menu_item_content_type,
            object_id=menu_item.id,
            attachment_file=get_dummy_uploaded_image("menu_item_thumbnail.png"),
            filetype=file_type,
            creator=self.user,
        )

        change_data = {
            "title_en": "I have a new thumbnail",
            "platform": "all",
            "_position": "first-child",
            "thumbnail-clear": "on",
        }

        response = self.client.post(
            f"/admin/flatpages/menuitem/{menu_item.id}/change/", data=change_data
        )

        self.assertEqual(response.status_code, 302)

        qs = Attachment.objects.filter(
            object_id=menu_item.id, content_type=menu_item_content_type
        ).all()
        self.assertEqual(len(qs), 0)
