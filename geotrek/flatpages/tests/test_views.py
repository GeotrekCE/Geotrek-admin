from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from geotrek.authent.models import User
from geotrek.common.models import FileType, Attachment
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.flatpages.models import MenuItem


# from geotrek.flatpages.tests.factories import FlatPageFactory


# TODO: to be removed, used for randov2 synchronization which is deprecated.
# class RESTViewsTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         FlatPageFactory.create_batch(10, published=True)
#         FlatPageFactory.create(published=False)
#
#     def test_records_list(self):
#         response = self.client.get('/api/en/flatpages.json')
#         self.assertEqual(response.status_code, 200)
#         records = response.json()
#         self.assertEqual(len(records), 10)
#
#     def test_serialized_attributes(self):
#         response = self.client.get('/api/en/flatpages.json')
#         records = response.json()
#         record = records[0]
#         self.assertEqual(
#             sorted(record.keys()),
#             sorted(['content', 'external_url', 'id', 'last_modified',
#                     'media', 'portal', 'publication_date', 'published',
#                     'published_status', 'slug', 'source', 'target',
#                     'title']))


class MenuItemAdminChangeFormView(TestCase):

    # TODO:
    # - [ok] test post Menu Item form works for addition
    # - [ok] test post Menu Item form works for change
    # - [ok] test post error if target_type = "page" and field "page" empty
    # - [ok] test post error if target_type = "link" and field "link_url" empty (for default language)
    # - test get form with thumbnail
    # - test post form with change of thumbnail
    # - test post form with deletion of thumbnail

    def setUp(self) -> None:
        self.user = User.objects.create(username="test_user", is_staff=True)
        add_perm = Permission.objects.get(codename="add_menuitem")
        view_perm = Permission.objects.get(codename="view_menuitem")
        update_perm = Permission.objects.get(codename="change_menuitem")
        delete_perm = Permission.objects.get(codename="delete_menuitem")
        self.user.user_permissions.add(add_perm, view_perm, update_perm, delete_perm)
        self.client.force_login(self.user)

    def test_menu_item_admin_form_add(self):
        add_data = {
            "label_en": "Hello World!",
            "platform": "all",
            "_position": "first-child",
        }

        response = self.client.post("/admin/flatpages/menuitem/add/", data=add_data, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(MenuItem.objects.filter(label_en="Hello World!").count(), 1)

    def test_menu_item_admin_form_change(self):
        menu_item = MenuItem.add_root(
            label_en="Already exists",
            platform="web",
        )

        change_data = {
            "label_en": "Already exists and changed",
            "platform": "mobile",
            "_position": "first-child",
        }

        response = self.client.post(f"/admin/flatpages/menuitem/{menu_item.id}/change/", data=change_data, follow=False)

        self.assertEqual(response.status_code, 302)
        changed_menu_item = MenuItem.objects.get(pk=menu_item.id)
        self.assertEqual(changed_menu_item.label_en, change_data["label_en"])
        self.assertEqual(changed_menu_item.platform, change_data["platform"])

    def test_menu_item_admin_form_page_required_error(self):
        add_data = {
            "label_en": "Hello World!",
            "platform": "all",
            "_position": "first-child",
            "target_type": "page",
            "page": "",
        }

        response = self.client.post("/admin/flatpages/menuitem/add/", data=add_data, follow=False)

        self.assertEqual(response.status_code, 200)
        adminform_errors = response.context["adminform"].errors
        self.assertTrue("page" in adminform_errors)
        self.assertTrue("required" in adminform_errors["page"][0])

    def test_menu_item_admin_form_link_url_required_error(self):
        link_url_loc_fieldname = "link_url_" + settings.MODELTRANSLATION_DEFAULT_LANGUAGE
        add_data = {
            "label_en": "Hello World!",
            "platform": "all",
            "_position": "first-child",
            "target_type": "link",
            link_url_loc_fieldname: "",
        }

        response = self.client.post("/admin/flatpages/menuitem/add/", data=add_data, follow=False)

        self.assertEqual(response.status_code, 200)
        adminform_errors = response.context["adminform"].errors
        self.assertTrue(link_url_loc_fieldname in adminform_errors)
        self.assertTrue("required" in adminform_errors[link_url_loc_fieldname][0])

    def test_menu_item_admin_form_retrieve_with_thumbnail(self):
        menu_item = MenuItem.add_root(
            label_en="I have a thumbnail",
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

    def test_menu_item_admin_form_change_thumbnail(self):
        menu_item = MenuItem.add_root(
            label_en="I have a thumbnail",
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
            "label_en": "I have a new thumbnail",
            "platform": "all",
            "_position": "first-child",
            "thumbnail": img,
        }

        response = self.client.post(f"/admin/flatpages/menuitem/{menu_item.id}/change/", data=change_data)

        self.assertEqual(response.status_code, 302)

        qs = Attachment.objects.filter(object_id=menu_item.id, content_type=menu_item_content_type).all()
        self.assertEqual(len(qs), 1)
        thumbnail = qs.first()
        self.assertIn("new_thumbnail", thumbnail.filename)

    def test_menu_item_admin_form_delete_thumbnail(self):
        menu_item = MenuItem.add_root(
            label_en="I have a thumbnail",
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
            "label_en": "I have a new thumbnail",
            "platform": "all",
            "_position": "first-child",
            "thumbnail-clear": "on",
        }

        response = self.client.post(f"/admin/flatpages/menuitem/{menu_item.id}/change/", data=change_data)

        self.assertEqual(response.status_code, 302)

        qs = Attachment.objects.filter(object_id=menu_item.id, content_type=menu_item_content_type).all()
        self.assertEqual(len(qs), 0)
