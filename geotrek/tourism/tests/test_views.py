from unittest import mock

from django.contrib.auth.models import Group, Permission

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from paperclip.models import random_suffix_regexp

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import (StructureFactory, UserFactory,
                                             UserProfileFactory)
from geotrek.common.models import Attachment, FileType
from geotrek.tourism.tests.factories import (InformationDeskFactory,
                                             TouristicContentCategoryFactory,
                                             TouristicContentFactory,
                                             TouristicEventFactory)
from geotrek.trekking.tests import factories as trekking_factories
from geotrek.trekking.tests.base import TrekkingManagerTest

PNG_BLACK_PIXEL = bytes.fromhex(
    '89504e470d0a1a0a0000000d4948445200000001000000010804000000b51c0c0200'
    '00000b4944415478da6364f80f00010501012718e3660000000049454e44ae426082'
)


class TouristicContentViewsSameStructureTests(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        cls.user = profile.user
        cls.user.groups.add(Group.objects.get(name="Référents communication"))
        cls.content1 = TouristicContentFactory.create()
        structure = StructureFactory.create()
        cls.content2 = TouristicContentFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(user=self.user)

    def tearDown(self):
        self.client.logout()

    def test_can_edit_same_structure(self):
        url = "/touristiccontent/edit/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = "/touristiccontent/edit/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/touristiccontent/{pk}/".format(pk=self.content2.pk))

    def test_can_delete_same_structure(self):
        url = "/touristiccontent/delete/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = "/touristiccontent/delete/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/touristiccontent/{pk}/".format(pk=self.content2.pk))

    def test_contents_on_treks_do_not_exist(self):
        response = self.client.get('api/en/treks/0/touristiccontents.geojson')
        self.assertEqual(response.status_code, 404)

    def test_contents_on_treks_not_public(self):
        trek = trekking_factories.TrekFactory.create(published=False)
        response = self.client.get('api/en/treks/{}/touristiccontents.geojson'.format(trek.pk))
        self.assertEqual(response.status_code, 404)


class TouristicContentTemplatesTest(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = TouristicContentFactory.create()
        cat = cls.content.category
        cat.type1_label = 'Michelin'
        cat.save()
        cls.category2 = TouristicContentCategoryFactory(label="Another category")

    def setUp(self):
        self.login()

    def tearDown(self):
        self.client.logout()

    def test_only_used_categories_are_shown(self):
        url = "/touristiccontent/list/"
        response = self.client.get(url)
        self.assertContains(response, 'title="Category"')
        self.assertNotContains(response, 'title="Another category"')

    def test_shown_in_details_when_enabled(self):
        url = "/touristiccontent/%s/" % self.content.pk
        response = self.client.get(url)
        self.assertContains(response, 'Tourism')

    @override_settings(TOURISM_ENABLED=False)
    def test_not_tourism_detail_fragment_displayed(self):
        """Test in other module, if tourism_detail_fragment.html is not displayed."""
        trek = trekking_factories.TrekFactory.create()
        url = "/trek/%s/" % trek.pk
        response = self.client.get(url)
        self.assertNotContains(response, 'Tourism')

    def test_type_label_shown_in_detail_page(self):
        url = "/touristiccontent/{pk}/".format(pk=self.content.pk)
        response = self.client.get(url)
        self.assertContains(response, 'Michelin', response.content)


class TouristicContentFormTest(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = TouristicContentCategoryFactory()

    def setUp(self):
        self.login()

    def test_no_category_selected_by_default(self):
        url = "/touristiccontent/add/"
        response = self.client.get(url)
        self.assertNotContains(response, 'value="%s" selected' % self.category.pk)

    def test_default_category_is_taken_from_url_params(self):
        url = "/touristiccontent/add/?category=%s" % self.category.pk
        response = self.client.get(url)
        self.assertContains(response, 'value="%s" selected' % self.category.pk)


class TouristicEventViewsSameStructureTests(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        cls.user = profile.user
        cls.user.groups.add(Group.objects.get(name="Référents communication"))

        cls.event1 = TouristicEventFactory.create()
        structure = StructureFactory.create()
        cls.event2 = TouristicEventFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_can_edit_same_structure(self):
        url = "/touristicevent/edit/{pk}/".format(pk=self.event1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = "/touristicevent/edit/{pk}/".format(pk=self.event2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/touristicevent/{pk}/".format(pk=self.event2.pk))

    def test_can_delete_same_structure(self):
        url = "/touristicevent/delete/{pk}/".format(pk=self.event1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = "/touristicevent/delete/{pk}/".format(pk=self.event2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/touristicevent/{pk}/".format(pk=self.event2.pk))

    def test_events_on_treks_do_not_exist(self):
        response = self.client.get('/api/en/treks/0/touristicevents.geojson')
        self.assertEqual(response.status_code, 404)

    def test_events_on_treks_not_public(self):
        trek = trekking_factories.TrekFactory.create(published=False)
        response = self.client.get('/api/en/treks/{}/touristicevents.geojson'.format(trek.pk))
        self.assertEqual(response.status_code, 404)


class TouristicContentCustomViewTests(TrekkingManagerTest):

    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        content = TouristicContentFactory.create(published=True)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_external_public_document_pdf(self):
        content = TouristicContentFactory.create(published=True)
        Attachment.objects.create(
            filetype=FileType.objects.create(type="Topoguide"),
            content_object=content,
            creator=UserFactory.create(),
            attachment_file=SimpleUploadedFile('external.pdf', b'External PDF')
        )
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        regexp = f"/media_secure/paperclip/tourism_touristiccontent/{content.pk}/external{random_suffix_regexp()}.pdf"
        self.assertRegex(response['X-Accel-Redirect'], regexp)

    @override_settings(ONLY_EXTERNAL_PUBLIC_PDF=True)
    def test_only_external_public_document_pdf(self):
        content = TouristicContentFactory.create(published=True)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_published_document_pdf(self):
        content = TouristicContentFactory.create(published=False)
        url = '/api/en/touristiccontents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TouristicEventOrganizerCreatePopupTest(TestCase):
    def test_cannot_create_organizer(self):
        url = '/popup/add/organizer/'
        response = self.client.get(url)
        # with no user logged -> redirect to login page
        self.assertRedirects(response, "/login/?next=/popup/add/organizer/")
        user = UserFactory()
        self.client.force_login(user=user)
        response = self.client.get(url)
        # with user with no perm -> redirect to login page
        self.assertEqual(response.status_code, 403)

    def test_can_create_organizer(self):
        user = UserFactory()
        user.user_permissions.add(Permission.objects.get(codename='add_touristiceventorganizer'))
        self.client.force_login(user=user)
        url = '/popup/add/organizer/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data={"label": "test"})
        self.assertIn("dismissAddAnotherPopup", response.content.decode())


class TouristicEventCustomViewTests(TrekkingManagerTest):
    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        content = TouristicEventFactory.create(published=True)
        url = '/api/en/touristicevents/{pk}/slug.pdf'.format(pk=content.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_not_published_document_pdf(self):
        content = TouristicEventFactory.create(published=False)
        url = '/api/en/touristicevents/{pk}/slug.pdf'.format(pk=content.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TrekInformationDeskAPITest(TestCase):
    def test_geojson(self):
        trek = trekking_factories.TrekFactory()
        desk = InformationDeskFactory.create()
        InformationDeskFactory.create()
        trek.information_desks.add(desk)
        trek.save()
        response = self.client.get('/api/en/treks/{}/information_desks.geojson'.format(trek.pk))
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result['features']), 1)
        self.assertEqual(result['features'][0]['type'], 'Feature')
        self.assertEqual(result['features'][0]['geometry']['type'], 'Point')
        self.assertEqual(result['features'][0]['properties']['name'], desk.name)
