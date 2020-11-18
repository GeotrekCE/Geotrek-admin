import os

from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase

from geotrek.authent.tests import AuthentFixturesTest
from geotrek.infrastructure.factories import InfrastructureTypeFactory, InfrastructureConditionFactory
from geotrek.infrastructure.models import InfrastructureType, InfrastructureCondition
from geotrek.authent.models import Structure
from geotrek.authent.factories import StructureFactory

from mapentity.factories import SuperUserFactory, UserFactory


class InfrastructureTypeAdminNoBypassTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create(password='booh')
        self.client.login(username=self.user.username, password='booh')
        self.user.user_permissions.add(Permission.objects.get(codename='add_draft_path'))
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            self.user.user_permissions.add(perm)
        self.user.is_staff = True
        self.user.save()
        p = self.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        self.infra = InfrastructureTypeFactory.create(structure=structure)

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_infrastructuretype_changelist(self):
        self.login()
        changelist_url = reverse('admin:infrastructure_infrastructuretype_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, InfrastructureType.objects.get(pk=self.infra.pk).label)

    def test_infrastructuretype_can_be_change(self):
        self.login()
        change_url = reverse('admin:infrastructure_infrastructuretype_change', args=[self.infra.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'type': 'A',
                                                 'pictogram': os.path.join(
                                                     settings.MEDIA_URL, self.infra.pictogram.name)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InfrastructureType.objects.get(pk=self.infra.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/infrastructure/infrastructuretype/')

    def test_infrastructuretype_cannot_be_change_not_same_structure(self):
        self.login()
        structure = StructureFactory(name="Other")
        infra = InfrastructureTypeFactory.create(structure=structure)
        change_url = reverse('admin:infrastructure_infrastructuretype_change', args=[infra.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InfrastructureType.objects.get(pk=self.infra.pk).label, self.infra.label)

        self.assertEqual(response.url, '/admin/')


class InfrastructureConditionAdminNoBypassTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create(password='booh')
        self.client.login(username=self.user.username, password='booh')
        self.user.user_permissions.add(Permission.objects.get(codename='add_draft_path'))
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            self.user.user_permissions.add(perm)
        self.user.is_staff = True
        self.user.save()
        p = self.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        self.infra = InfrastructureConditionFactory.create(structure=structure)

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_infrastructurecondition_changelist(self):
        self.login()
        changelist_url = reverse('admin:infrastructure_infrastructurecondition_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, InfrastructureCondition.objects.get(pk=self.infra.pk).label)

    def test_infrastructurecondition_can_be_change(self):
        self.login()
        change_url = reverse('admin:infrastructure_infrastructurecondition_change', args=[self.infra.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'structure': Structure.objects.first().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InfrastructureCondition.objects.get(pk=self.infra.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/infrastructure/infrastructurecondition/')

    def test_infrastructurecondition_cannot_be_change_not_same_structure(self):
        self.login()
        structure = StructureFactory(name="Other")
        infra = InfrastructureConditionFactory.create(structure=structure)
        change_url = reverse('admin:infrastructure_infrastructurecondition_change', args=[infra.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InfrastructureCondition.objects.get(pk=self.infra.pk).label, self.infra.label)

        self.assertEqual(response.url, '/admin/')


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
        response = self.client.post(change_url, {'label': 'coucou', 'type': 'A',
                                                 'pictogram': os.path.join(
                                                     settings.MEDIA_URL, self.infra.pictogram.name)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InfrastructureType.objects.get(pk=self.infra.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/infrastructure/infrastructuretype/')

    def test_infrastructuretype_changelist(self):
        self.login()
        changelist_url = reverse('admin:infrastructure_infrastructuretype_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, InfrastructureType.objects.get(pk=self.infra.pk).label)


class InfrastructureConditionAdminTest(AuthentFixturesTest):
    def setUp(self):
        StructureFactory.create()
        self.user = SuperUserFactory.create(password='booh')
        self.infra = InfrastructureConditionFactory.create()

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_infrastructurecondition_can_be_change(self):
        self.login()

        change_url = reverse('admin:infrastructure_infrastructurecondition_change', args=[self.infra.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'structure': Structure.objects.first().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InfrastructureCondition.objects.get(pk=self.infra.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/infrastructure/infrastructurecondition/')

    def test_infrastructurecondition_changelist(self):
        self.login()
        changelist_url = reverse('admin:infrastructure_infrastructurecondition_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, InfrastructureCondition.objects.get(pk=self.infra.pk).label)
