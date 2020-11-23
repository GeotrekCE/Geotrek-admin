import os

from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase

from geotrek.authent.tests import AuthentFixturesTest
from geotrek.signage.factories import (SealingFactory, SignageTypeFactory, BladeColorFactory,
                                       BladeDirectionFactory, BladeTypeFactory)
from geotrek.signage.models import SignageType, Sealing, Color, Direction, BladeType
from geotrek.authent.factories import StructureFactory

from mapentity.factories import SuperUserFactory, UserFactory


class SignageTypeAdminNoBypassTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create(password='booh')
        self.client.login(username=self.user.username, password='booh')
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            self.user.user_permissions.add(perm)
        self.user.is_staff = True
        self.user.save()
        p = self.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        self.signa = SignageTypeFactory.create(structure=structure)

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_signagetype_changelist(self):
        self.login()
        changelist_url = reverse('admin:signage_signagetype_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, SignageType.objects.get(pk=self.signa.pk).label)

    def test_signagetype_can_be_change(self):
        self.login()
        change_url = reverse('admin:signage_signagetype_change', args=[self.signa.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'type': 'A',
                                                 'pictogram': os.path.join(
                                                     settings.MEDIA_URL, self.signa.pictogram.name)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SignageType.objects.get(pk=self.signa.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/signage/signagetype/')

    def test_signage_type_change_not_same_structure(self):
        self.login()
        structure = StructureFactory(name="Other")
        infra = SignageTypeFactory.create(structure=structure)
        change_url = reverse('admin:signage_signagetype_change', args=[infra.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SignageType.objects.get(pk=self.signa.pk).label, self.signa.label)

        self.assertEqual(response.url, '/admin/')


class SealingAdminNoBypassTest(AuthentFixturesTest):
    def setUp(self):
        self.user = UserFactory.create(password='booh')
        self.client.login(username=self.user.username, password='booh')
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            self.user.user_permissions.add(perm)
        self.user.is_staff = True
        self.user.save()
        p = self.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        self.sealing = SealingFactory.create(structure=structure)

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_sealing_changelist(self):
        self.login()
        changelist_url = reverse('admin:signage_sealing_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Sealing.objects.get(pk=self.sealing.pk).label)

    def test_sealing_can_be_change(self):
        self.login()
        change_url = reverse('admin:signage_sealing_change', args=[self.sealing.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'structure': StructureFactory.create().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sealing.objects.get(pk=self.sealing.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/signage/sealing/')

    def test_sealing_change_not_same_structure(self):
        self.login()
        structure = StructureFactory(name="Other")
        sealing = SealingFactory.create(structure=structure)
        change_url = reverse('admin:signage_sealing_change', args=[sealing.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sealing.objects.get(pk=self.sealing.pk).label, self.sealing.label)

        self.assertEqual(response.url, '/admin/')


class ColorAdminNoBypassTest(AuthentFixturesTest):
    def setUp(self):
        self.user = SuperUserFactory.create(password='booh')
        self.color = BladeColorFactory.create()

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_color_changelist(self):
        self.login()
        changelist_url = reverse('admin:signage_color_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Color.objects.get(pk=self.color.pk).label)

    def test_color_can_be_change(self):
        self.login()
        change_url = reverse('admin:signage_color_change', args=[self.color.pk])
        response = self.client.post(change_url, {'label': 'coucou'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Color.objects.get(pk=self.color.pk).label, 'coucou')
        self.assertEqual(response.url, '/admin/signage/color/')


class DirectionAdminNoBypassTest(AuthentFixturesTest):
    def setUp(self):
        self.user = SuperUserFactory.create(password='booh')
        self.direction = BladeDirectionFactory.create()

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_direction_changelist(self):
        self.login()
        changelist_url = reverse('admin:signage_direction_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Direction.objects.get(pk=self.direction.pk).label)

    def test_direction_can_be_change(self):
        self.login()
        change_url = reverse('admin:signage_direction_change', args=[self.direction.pk])
        response = self.client.post(change_url, {'label': 'coucou'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Direction.objects.get(pk=self.direction.pk).label, 'coucou')
        self.assertEqual(response.url, '/admin/signage/direction/')


class BladeTypeAdminNoBypassTest(AuthentFixturesTest):
    def setUp(self):
        self.user = UserFactory.create(password='booh')
        self.client.login(username=self.user.username, password='booh')
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            self.user.user_permissions.add(perm)
        self.user.is_staff = True
        self.user.save()
        p = self.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        self.bladetype = BladeTypeFactory.create(structure=structure)

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_bladetype_changelist(self):
        self.login()
        changelist_url = reverse('admin:signage_bladetype_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, BladeType.objects.get(pk=self.bladetype.pk).label)

    def test_bladetype_can_be_change(self):
        self.login()
        change_url = reverse('admin:signage_bladetype_change', args=[self.bladetype.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'structure': StructureFactory.create().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BladeType.objects.get(pk=self.bladetype.pk).label, 'coucou')

        self.assertEqual(response.url, '/admin/signage/bladetype/')

    def test_bladetype_change_not_same_structure(self):
        self.login()
        structure = StructureFactory(name="Other")
        bladetype = BladeTypeFactory.create(structure=structure)
        change_url = reverse('admin:signage_bladetype_change', args=[bladetype.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BladeType.objects.get(pk=self.bladetype.pk).label, self.bladetype.label)

        self.assertEqual(response.url, '/admin/')


class BladeTypeAdminTest(BladeTypeAdminNoBypassTest):
    def setUp(self):
        super(BladeTypeAdminTest, self).setUp()
        perm_bypass = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm_bypass)

    def test_bladetype_change_not_same_structure(self):
        self.login()
        structure = StructureFactory(name="Other")
        bladetype = BladeTypeFactory.create(structure=structure)
        change_url = reverse('admin:signage_bladetype_change', args=[bladetype.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="structure" id="id_structure">')


class SealingAdminTest(SealingAdminNoBypassTest):
    def setUp(self):
        super(SealingAdminTest, self).setUp()
        perm_bypass = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm_bypass)

    def test_sealing_change_not_same_structure(self):
        self.login()
        structure = StructureFactory(name="Other")
        sealing = SealingFactory.create(structure=structure)
        change_url = reverse('admin:signage_sealing_change', args=[sealing.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="structure" id="id_structure">')


class SignageTypeAdminTest(SignageTypeAdminNoBypassTest):
    def setUp(self):
        super(SignageTypeAdminTest, self).setUp()
        perm_bypass = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm_bypass)

    def test_signage_type_change_not_same_structure(self):
        self.login()
        structure = StructureFactory(name="Other")
        signagetype = SignageTypeFactory.create(structure=structure)
        change_url = reverse('admin:signage_signagetype_change', args=[signagetype.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="structure" id="id_structure">')
