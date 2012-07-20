from collections import namedtuple

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import translation


from caminae.maintenance.models import InterventionStatus
from caminae.authent.models import default_structure


Credential = namedtuple('Credential', ['username', 'password'])

def create_superuser_from_cred(cred, email='admin@admin.com'):
    return User.objects.create_superuser(cred.username, email, cred.password)

def login_from_cred(client, cred):
    return client.login(**cred._asdict())


## Admin related

def admin_add_url_from_model(model):
    info = model._meta.app_label, model._meta.module_name
    return reverse('admin:%s_%s_add' % info)

def admin_list_url_from_model(model):
    info = model._meta.app_label, model._meta.module_name
    return reverse('admin:%s_%s_changelist' % info)

# modeladmin = admin.site._registry[InterventionStatus]
# form = modeladmin.get_form(response._request)


class TraductionTestCase(TestCase):
    """
    Test a superuser has access to the InterventionStatus and can enter a translation
    """

    def setUp(self):
        """
            Create credential and associated superuser
        """
        self.cred = Credential('admin', 'adminpass')
        self.superuser = create_superuser_from_cred(self.cred)
        admin.autodiscover()

    @classmethod
    def get_dummy_status_trad(cls):
        return dict(
            status=u"status_default",
            status_en=u"status_en",
            status_fr=u"status_fr",
            status_it=u"status_it",
        )

    def test_admin_set_trad(self):
        # Given no InterventionStatus is present in the database
        self.assertEquals(InterventionStatus.objects.all().count(), 0)

        # login
        success = login_from_cred(self.client, self.cred)
        self.assertTrue(success)

        add_intervention_url = admin_add_url_from_model(InterventionStatus)

        response = self.client.get(add_intervention_url)
        self.assertEquals(response.status_code, 200)

        # Get data for InterventionStatus creation and create it through admin view
        data = dict(structure=default_structure().pk, code=1234,)
        data.update(self.get_dummy_status_trad())

        response = self.client.post(add_intervention_url, data, follow=True)
        self.assertRedirects(response, admin_list_url_from_model(InterventionStatus))
        self.assertEquals(response.status_code, 200)

        iss = InterventionStatus.objects.all()
        self.assertEquals(len(iss), 1, "One and only one InterventionStatus should be created")

        # This may test too much.
        # Test language translation for intervention_status.status works
        # Given the language set, it returns the appropriate version (fr, it, en)

        orig_language = translation.get_language_from_request(response._request)
        restore_language = lambda: translation.activate(orig_language)

        status_trad = self.get_dummy_status_trad()
        intervention_status = iss[0]

        for language in ('fr', 'it', 'en'):
            translation.activate(language)
            translated_status = status_trad['status_%s' % language]
            self.assertEquals(intervention_status.status, translated_status)

        restore_language()




