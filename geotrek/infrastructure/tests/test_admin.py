from django.core.urlresolvers import reverse

from geotrek.authent.tests import AuthentFixturesTest
from geotrek.infrastructure.factories import InfrastructureTypeFactory, InfrastructureConditionFactory
from geotrek.infrastructure.models import InfrastructureType, InfrastructureCondition
from geotrek.authent.models import Structure

from mapentity.factories import SuperUserFactory


class InfrastructureTypeAdminTest(AuthentFixturesTest):
    def setUp(self):
        self.user = SuperUserFactory.create(password='booh')
        self.infra = InfrastructureTypeFactory.create()

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_infrastructuretype_can_be_change(self):
        self.login()
        change_url = reverse('admin:infrastructure_infrastructuretype_change', args=[self.infra.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'type': 'A'})
        self.assertEquals(response.status_code, 302)
        self.assertEqual(InfrastructureType.objects.get(pk=self.infra.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/infrastructure/infrastructuretype/')

    def test_infrastructuretype_changelist(self):
        self.login()
        changelist_url = reverse('admin:infrastructure_infrastructuretype_changelist')
        response = self.client.get(changelist_url)
        self.assertContains(response, InfrastructureType.objects.get(pk=self.infra.pk).label)


class InfrastructureConditionAdminTest(AuthentFixturesTest):
    def setUp(self):
        self.user = SuperUserFactory.create(password='booh')
        self.infra = InfrastructureConditionFactory.create()

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_infrastructuretype_can_be_change(self):
        self.login()

        change_url = reverse('admin:infrastructure_infrastructurecondition_change', args=[self.infra.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'structure': Structure.objects.first().pk})
        self.assertEquals(response.status_code, 302)
        self.assertEqual(InfrastructureCondition.objects.get(pk=self.infra.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/infrastructure/infrastructurecondition/')

    def test_infrastructuretype_changelist(self):
        self.login()
        changelist_url = reverse('admin:infrastructure_infrastructurecondition_changelist')
        response = self.client.get(changelist_url)
        self.assertContains(response, InfrastructureCondition.objects.get(pk=self.infra.pk).label)
