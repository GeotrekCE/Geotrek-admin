from collections import namedtuple

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import translation


from geotrek.common.utils.testdata import get_dummy_uploaded_file
from geotrek.trekking.models import DifficultyLevel


Credential = namedtuple('Credential', ['username', 'password'])


def create_superuser_from_cred(cred, email='admin@admin.com'):
    return User.objects.create_superuser(cred.username, email, cred.password)


def login_from_cred(client, cred):
    return client.login(**cred._asdict())


def admin_add_url_from_model(model):
    info = model._meta.app_label, model._meta.model_name
    return reverse('admin:%s_%s_add' % info)


def admin_list_url_from_model(model):
    info = model._meta.app_label, model._meta.model_name
    return reverse('admin:%s_%s_changelist' % info)


class TraductionTestCase(TestCase):
    """
    Test a superuser has access to the DifficultyLevel and can enter a translation
    """

    def setUp(self):
        """
            Create credential and associated superuser
        """
        self.cred = Credential('admin', 'adminpass')
        self.superuser = create_superuser_from_cred(self.cred)

    @classmethod
    def get_dummy_data_trad(cls):
        return dict(
            id=1,
            difficulty=u"difficulty_descr_default",
            difficulty_en=u"difficulty_descr_en",
            difficulty_fr=u"difficulty_descr_fr",
            difficulty_it=u"difficulty_descr_it",
            pictogram=get_dummy_uploaded_file()
        )

    def test_admin_set_trad(self):
        # Given no DifficultyLevel is present in the database
        self.assertEquals(DifficultyLevel.objects.all().count(), 0)

        # login
        success = login_from_cred(self.client, self.cred)
        self.assertTrue(success)

        add_difficulty_url = admin_add_url_from_model(DifficultyLevel)

        response = self.client.get(add_difficulty_url)
        self.assertEquals(response.status_code, 200)

        # Get data for DifficultyLevel creation and create it through admin view
        data = self.get_dummy_data_trad()

        response = self.client.post(add_difficulty_url, data, follow=True)
        self.assertRedirects(response, admin_list_url_from_model(DifficultyLevel))
        self.assertEquals(response.status_code, 200)

        iss = DifficultyLevel.objects.all()
        self.assertEquals(len(iss), 1, "One and only one DifficultyLevel should be created")

        # This may test too much.
        # Test language translation for DifficultyLevel.difficulty works
        # Given the language set, it returns the appropriate version (fr, it, en)

        orig_language = translation.get_language_from_request(response._request)

        difficulty_trad = self.get_dummy_data_trad()
        intervention_difficulty = iss[0]

        for language in ('fr', 'it', 'en'):
            translation.activate(language)
            translated_difficulty = difficulty_trad['difficulty_%s' % language]
            self.assertEquals(intervention_difficulty.difficulty, translated_difficulty)

        translation.activate(orig_language)
