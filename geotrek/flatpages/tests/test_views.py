from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from geotrek.authent.models import User
from geotrek.authent.tests.factories import UserProfileFactory
from geotrek.common.models import FileType, Attachment
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.flatpages.models import MenuItem, FlatPage


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


def _flatten(fieldsets):
    fields = []
    for fieldset in fieldsets:
        for field in fieldset[1]["fields"]:
            fields.append(field)
    return fields


class MenuItemAdminChangeFormView(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username="test_user", is_staff=True)
        add_perm = Permission.objects.get(codename="add_menuitem")
        view_perm = Permission.objects.get(codename="view_menuitem")
        update_perm = Permission.objects.get(codename="change_menuitem")
        delete_perm = Permission.objects.get(codename="delete_menuitem")
        self.user.user_permissions.add(add_perm, view_perm, update_perm, delete_perm)
        self.client.force_login(self.user)

    def test_menu_item_retrieve_expected_form_fields(self):
        url = reverse('admin:flatpages_menuitem_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        expected_fields = [
            "label_en",
            "label_fr",
            "label_es",
            "label_it",
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


class FlatPageAdminChangeFormView(TestCase):
    def login(self):
        profile = UserProfileFactory(
            user__username='spammer',
            user__password='pipo'
        )
        user = profile.user

        # Gives permissions to access AdminSite and to CRUD FlatPages
        user.is_staff = True
        user.save()
        add_perm = Permission.objects.get(codename="add_flatpage")
        view_perm = Permission.objects.get(codename="view_flatpage")
        update_perm = Permission.objects.get(codename="change_flatpage")
        delete_perm = Permission.objects.get(codename="delete_flatpage")
        user.user_permissions.add(add_perm, view_perm, update_perm, delete_perm)

        success = self.client.login(username=user.username, password='pipo')
        self.assertTrue(success)
        return user

    def test_retrieve_expected_form_fields(self):
        self.login()

        url = reverse('admin:flatpages_flatpage_add')
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
        self.login()
        data = {
            "title_en": "Hello English World!",
            "_position": "first-child",
        }
        url = reverse('admin:flatpages_flatpage_add')
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FlatPage.objects.count(), 1)
        page = FlatPage.objects.get()
        self.assertEqual(page.title, 'Hello English World!')

    def test_save_with_cover_image(self):
        self.login()

        with get_dummy_uploaded_image().open() as image_file:
            data = {
                "title_en": "Hello World!",
                "_position": "first-child",
                "cover_image": image_file,
                'cover_image_author': 'Someone',
            }
            url = reverse('admin:flatpages_flatpage_add')
            response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FlatPage.objects.count(), 1)
        page = FlatPage.objects.get()
        self.assertEqual(Attachment.objects.count(), 1)
        attachment = Attachment.objects.get()
        self.assertEqual(attachment.content_object, page)
        self.assertEqual(attachment.author, 'Someone')

    def test_save_delete_cover_image(self):
        user = self.login()
        page = FlatPage(
            title='Title',
        )
        FlatPage.add_root(instance=page)
        page.save()
        filetype = FileType.objects.create(type="Photographie")
        Attachment.objects.create(
            content_object=page,
            attachment_file=get_dummy_uploaded_image(),
            author='Someone',
            filetype=filetype,
            creator=user
        )

        url = reverse('admin:flatpages_flatpage_change', args=[page.pk])
        response = self.client.post(url, data={
            "title_en": "Hello World!",
            "_position": "first-child",
            'cover_image-clear': 'on',
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Attachment.objects.exists())
