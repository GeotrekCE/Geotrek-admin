from django.core.urlresolvers import reverse

from geotrek.authent.tests import AuthentFixturesTest
from geotrek.authent.factories import TrekkingManagerFactory

from ..models import Trek
from ..factories import TrekFactory, DifficultyLevelFactory


class DifficultyLevelTest(AuthentFixturesTest):
    def setUp(self):
        self.user = TrekkingManagerFactory.create(password='booh')
        self.difficulty = DifficultyLevelFactory.create()
        self.trek = TrekFactory.create(difficulty=self.difficulty)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def get_csrf_token(self, response):
        csrf = "name='csrfmiddlewaretoken' value='"
        start = response.content.find(csrf) + len(csrf)
        end = response.content.find("'", start)
        return response.content[start:end]

    def test_cant_create_duplicate_id(self):
        self.login()
        response = self.client.get(reverse('admin:trekking_difficultylevel_add'))
        csrf = self.get_csrf_token(response)
        post_data = {'id': self.difficulty.pk,
                     'difficulty_fr': 'Dur-dur',
                     'csrfmiddlewaretoken': csrf}

        response = self.client.post(reverse('admin:trekking_difficultylevel_add'), post_data)
        error_msg = "Difficulty with id &#39;%s&#39; already exists" % self.difficulty.pk
        self.assertContains(response, error_msg)

    def test_migrate_trek_difficulty(self):
        self.login()
        self.assertEquals(self.trek.difficulty, self.difficulty)
        self.assertEquals(self.trek.difficulty_id, self.difficulty.pk)
        response = self.client.get(reverse('admin:trekking_difficultylevel_change', args=[self.difficulty.pk]))
        csrf = self.get_csrf_token(response)
        post_data = {'id': 4,
                     'difficulty_en': 'Dur-dur',
                     'csrfmiddlewaretoken': csrf}
        response = self.client.post(reverse('admin:trekking_difficultylevel_change', args=[self.difficulty.pk]), post_data)
        self.assertRedirects(response, reverse('admin:trekking_difficultylevel_changelist'))
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertNotEquals(trek.difficulty, self.difficulty)
        self.assertEquals(trek.difficulty_id, 4)


class DeleteObjectTest(AuthentFixturesTest):
    def setUp(self):
        self.user = TrekkingManagerFactory.create(password='booh')
        self.difficulty = DifficultyLevelFactory.create()
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_weblink_can_be_deleted(self):
        detail_url = reverse('admin:trekking_difficultylevel_change', args=[self.difficulty.pk])
        delete_url = reverse('admin:trekking_difficultylevel_delete', args=[self.difficulty.pk])
        response = self.client.post(delete_url, {'post': 'yes'})
        self.assertEquals(response.status_code, 302)
        response = self.client.get(detail_url)
        self.assertEquals(response.status_code, 404)
