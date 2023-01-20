from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse
from tempfile import TemporaryDirectory

from geotrek.common.models import Attachment, FileType, Theme
from geotrek.common.tests.factories import AttachmentFactory, HDViewPointFactory, ThemeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.trekking.models import DifficultyLevel, POI, Trek
from geotrek.trekking.tests.factories import DifficultyLevelFactory, POIFactory, TrekFactory
from mapentity.tests.factories import SuperUserFactory


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class AttachmentAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory()
        cls.poi = POIFactory.create(geom='SRID=%s;POINT(1 1)' % settings.SRID)
        cls.picture = AttachmentFactory(content_object=cls.poi, title='img1',
                                        attachment_file=get_dummy_uploaded_image())
        cls.trek = TrekFactory.create(geom='SRID=%s;LINESTRING(0 0, 1 0, 2 0)' % settings.SRID)
        cls.picture_2 = AttachmentFactory(content_object=cls.trek, title='img2',
                                          attachment_file=get_dummy_uploaded_image())
        cls.theme = ThemeFactory.create(label="Theme 1")
        cls.picture_3 = AttachmentFactory(content_object=cls.theme, title='img3',
                                          attachment_file=get_dummy_uploaded_image())

    def setUp(self):
        self.client.force_login(self.user)

    def test_changelist_attachment(self):
        list_url = reverse('admin:common_attachment_changelist')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('img1', self.picture.filename)
        self.assertIn('.png', self.picture.filename)
        self.assertIn('img2', self.picture_2.filename)
        self.assertIn('.png', self.picture_2.filename)
        self.assertContains(response, self.picture.filename)
        self.assertContains(response, self.picture_2.filename)
        self.assertContains(response, self.poi.get_detail_url())
        self.assertContains(response, self.trek.get_detail_url())
        self.assertContains(response, self.theme.pk)

    def test_changelist_attachment_filter_content_id(self):
        list_url = reverse('admin:common_attachment_changelist')
        data = {
            'content_type': ContentType.objects.get_for_model(POI).pk
        }

        response = self.client.get(list_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.picture.filename)
        self.assertNotContains(response, self.picture_2.filename)

    def test_attachment_can_be_change(self):
        change_url = reverse('admin:common_attachment_change', args=[self.picture.pk])
        file_type = FileType.objects.first()
        response = self.client.post(change_url, {'title': 'Coucou', 'filetype': file_type.pk, 'starred': True})
        self.assertEqual(response.status_code, 302)
        attachment_modified = Attachment.objects.get(pk=self.picture.pk)
        self.assertEqual(attachment_modified.title, self.picture.title)
        # Is not changed depend on file title
        self.assertEqual(attachment_modified.starred, True)
        self.assertEqual(response.url, reverse('admin:common_attachment_changelist'))


class MergeActionAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.theme = ThemeFactory.create(label="Theme 1")
        cls.theme_2 = ThemeFactory.create(label="Theme 2")
        cls.theme_other = ThemeFactory.create(label="Autre theme")
        cls.difficulty_1 = DifficultyLevelFactory.create(difficulty="Dif 1")
        cls.difficulty_2 = DifficultyLevelFactory.create(difficulty="Dif 2")
        cls.difficulty_3 = DifficultyLevelFactory.create(difficulty="Dif 3")
        cls.trek = TrekFactory.create(geom='SRID=%s;LINESTRING(0 0, 1 0, 2 0)' % settings.SRID,
                                      difficulty=cls.difficulty_2)
        cls.trek.themes.add(cls.theme, cls.theme_2)

    def setUp(self):
        self.client.force_login(self.user)

    def test_merge_actions_many2many(self):
        """
        (A B C)
         | | |
           T

        B main
        A C tail
        T linked only to B only
        """
        data = {'action': 'apply_merge', '_selected_action': Theme.objects.all().values_list('pk', flat=True)}
        self.client.post(reverse("admin:common_theme_changelist"), data, follow=True)
        self.assertEqual(Theme.objects.count(), 1)
        self.assertEqual(Theme.objects.first().label, "Autre theme + Theme 1 + Theme 2")
        self.assertEqual(self.trek.themes.first().label, "Autre theme + Theme 1 + Theme 2")

    def test_merge_actions_2_many2many(self):
        """
        (A B) C
           | /
           T

        A main
        B tail
        T linked to A after merge and C
        """
        data = {'action': 'apply_merge', '_selected_action': Theme.objects.filter(label__in=['Theme 1', 'Autre theme']).values_list('pk', flat=True)}
        self.client.post(reverse("admin:common_theme_changelist"), data, follow=True)
        self.assertEqual(Theme.objects.count(), 2)
        self.assertEqual(Theme.objects.exclude(label="Theme 2").first().label, "Autre theme + Theme 1")
        self.assertEqual(self.trek.themes.first().label, "Autre theme + Theme 1")

    def test_merge_actions_fk(self):
        """
        (A B) C
           |
           T

        A main
        B tail
        T linked to A
        """
        data = {'action': 'apply_merge', '_selected_action': DifficultyLevel.objects.filter(difficulty__in=['Dif 1', 'Dif 2']).values_list('pk', flat=True)}
        self.client.post(reverse("admin:trekking_difficultylevel_changelist"), data, follow=True)
        self.assertEqual(DifficultyLevel.objects.count(), 2)
        self.assertEqual(DifficultyLevel.objects.exclude(difficulty="Dif 3").first().difficulty, "Dif 1 + Dif 2")
        self.assertEqual(Trek.objects.first().difficulty.difficulty, "Dif 1 + Dif 2")

    def test_merge_actions_one_element(self):
        """
        A (B) C
           |
           T

        A main
        no tail
        T linked to A
        """
        data = {'action': 'apply_merge', '_selected_action': DifficultyLevel.objects.filter(difficulty="Dif 1").values_list('pk', flat=True)}
        self.client.post(reverse("admin:trekking_difficultylevel_changelist"), data, follow=True)
        self.assertEqual(DifficultyLevel.objects.count(), 3)

    def test_merge_actions_long_name(self):
        """
        (A B C)
         | | |
           T

        B main
        A C tail
        T linked only to B only
        """
        self.theme.label = '*' * 128
        self.theme.save()
        data = {'action': 'apply_merge', '_selected_action': Theme.objects.all().values_list('pk', flat=True)}
        self.client.post(reverse("admin:common_theme_changelist"), data, follow=True)
        self.assertEqual(Theme.objects.count(), 1)
        self.assertEqual(len(Theme.objects.first().label), 128)
        self.assertEqual(Theme.objects.first().label,
                         "*********************************************************************************************"
                         "******************************* ...")
        self.assertEqual(self.trek.themes.first().label,
                         "*********************************************************************************************"
                         "******************************* ...")


class HDViewPointAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory()
        cls.trek = TrekFactory()
        cls.vp = HDViewPointFactory(content_object=cls.trek)

    def setUp(self):
        self.client.force_login(self.user)

    def test_changelist_hdviewpoint(self):
        list_url = reverse('admin:common_hdviewpoint_changelist')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<a data-pk="{self.trek.pk}" href="{self.trek.get_detail_url()}" >{str(self.trek)}</a>')
        self.assertContains(response, f'<a data-pk="{self.vp.pk}" href="{self.vp.full_url}" >{self.vp.title}</a>')
