from django.contrib.auth.models import Permission
from django.test import TestCase
from geotrek.authent.models import User
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
    # - test post error if target_type = "link" and field "link_url" empty (for default language)
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
