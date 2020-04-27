from django.urls import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from geotrek.common.factories import AttachmentFactory, ThemeFactory
from geotrek.common.models import Attachment, FileType, Theme
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.trekking.models import DifficultyLevel, Trek
from geotrek.trekking.factories import DifficultyLevelFactory, POIFactory, TrekFactory

from mapentity.factories import SuperUserFactory


class AttachmentAdminTest(TestCase):
    def setUp(self):
        self.user = SuperUserFactory.create(password='booh')
        self.content = POIFactory.create(geom='SRID=%s;POINT(1 1)' % settings.SRID)

        self.picture = AttachmentFactory(content_object=self.content,
                                         attachment_file=get_dummy_uploaded_image(), )
        self.trek = TrekFactory.create(geom='SRID=%s;LINESTRING(0 0, 1 0, 2 0)' % settings.SRID)
        self.picture_2 = AttachmentFactory(content_object=self.trek,
                                           attachment_file=get_dummy_uploaded_image(), )

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_changelist_attachment(self):
        self.login()
        list_url = reverse('admin:common_attachment_changelist')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Attachment.objects.get(pk=self.picture.pk).title)
        self.assertContains(response, Attachment.objects.get(pk=self.picture_2.pk).title)

    def test_changelist_attachment_filter_content_id(self):
        self.login()
        list_url = reverse('admin:common_attachment_changelist')
        data = {
            'content_type': ContentType.objects.get(model='poi').pk
        }

        response = self.client.get(list_url, data)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, Attachment.objects.get(pk=self.picture.pk).title)
        self.assertNotContains(response, Attachment.objects.get(pk=self.picture_2.pk).title)

    def test_attachment_can_be_change(self):
        self.login()
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
    def setUp(self):
        self.user = SuperUserFactory.create(password='booh')

        self.theme = ThemeFactory.create(label="Theme 1")
        self.theme_2 = ThemeFactory.create(label="Theme 2")
        self.theme_other = ThemeFactory.create(label="Autre theme")
        self.difficulty_1 = DifficultyLevelFactory.create(difficulty="Dif 1")
        self.difficulty_2 = DifficultyLevelFactory.create(difficulty="Dif 2")
        self.difficulty_3 = DifficultyLevelFactory.create(difficulty="Dif 3")
        self.trek = TrekFactory.create(geom='SRID=%s;LINESTRING(0 0, 1 0, 2 0)' % settings.SRID,
                                       difficulty=self.difficulty_2)
        self.trek.themes.add(self.theme, self.theme_2)

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def test_merge_actions_many2many(self):
        """
        (A B C)
          \|/
           T

        B main
        C tail
        T linked only to B only
        """
        self.login()
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
        self.login()
        data = {'action': 'apply_merge', '_selected_action': Theme.objects.filter(label__in=['Theme 1', 'Autre theme'])
            .values_list('pk', flat=True)}
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
        self.login()
        data = {'action': 'apply_merge', '_selected_action': DifficultyLevel.objects.filter(difficulty__in=['Dif 1', 'Dif 2'])
            .values_list('pk', flat=True)}
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
        self.login()
        data = {'action': 'apply_merge', '_selected_action': DifficultyLevel.objects.filter(difficulty="Dif 1").values_list('pk', flat=True)}
        self.client.post(reverse("admin:trekking_difficultylevel_changelist"), data, follow=True)
        self.assertEqual(DifficultyLevel.objects.count(), 3)
