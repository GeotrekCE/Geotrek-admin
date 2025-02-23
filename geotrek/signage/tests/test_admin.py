import os
from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import StructureFactory
from geotrek.signage.models import SignageType, Sealing, Color, Direction, BladeType, SignageCondition
from geotrek.signage.tests.factories import (SealingFactory, SignageTypeFactory, BladeColorFactory,
                                             BladeDirectionFactory, BladeTypeFactory, SignageConditionFactory)
from mapentity.tests.factories import SuperUserFactory, UserFactory


class SignageTypeAdminNoBypassTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(is_staff=True)
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            cls.user.user_permissions.add(perm)
        p = cls.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        cls.signage_type = SignageTypeFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(self.user)

    def test_signage_type_changelist(self):
        changelist_url = reverse('admin:signage_signagetype_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, SignageType.objects.get(pk=self.signage_type.pk).label)

    def test_signage_type_can_be_change(self):
        change_url = reverse('admin:signage_signagetype_change', args=[self.signage_type.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'type': 'A',
                                                 'pictogram': os.path.join(
                                                     settings.MEDIA_URL, self.signage_type.pictogram.name)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SignageType.objects.get(pk=self.signage_type.pk).label, 'coucou')
        self.assertEqual(response.url, '/admin/signage/signagetype/')

    def test_signage_type_change_not_same_structure(self):
        structure = StructureFactory(name="Other")
        infra = SignageTypeFactory.create(structure=structure)
        change_url = reverse('admin:signage_signagetype_change', args=[infra.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SignageType.objects.get(pk=self.signage_type.pk).label, self.signage_type.label)
        self.assertEqual(response.url, '/admin/')


class SealingAdminNoBypassTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(is_staff=True)
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            cls.user.user_permissions.add(perm)
        p = cls.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        cls.sealing = SealingFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(self.user)

    def test_sealing_changelist(self):
        changelist_url = reverse('admin:signage_sealing_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Sealing.objects.get(pk=self.sealing.pk).label)

    def test_sealing_can_be_change(self):
        change_url = reverse('admin:signage_sealing_change', args=[self.sealing.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'structure': StructureFactory.create().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sealing.objects.get(pk=self.sealing.pk).label, 'coucou')
        self.assertEqual(response.url, '/admin/signage/sealing/')

    def test_sealing_change_not_same_structure(self):
        structure = StructureFactory(name="Other")
        sealing = SealingFactory.create(structure=structure)
        change_url = reverse('admin:signage_sealing_change', args=[sealing.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sealing.objects.get(pk=self.sealing.pk).label, self.sealing.label)
        self.assertEqual(response.url, '/admin/')


class ColorAdminNoBypassTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.color = BladeColorFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_color_changelist(self):
        changelist_url = reverse('admin:signage_color_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Color.objects.get(pk=self.color.pk).label)

    def test_color_can_be_change(self):
        change_url = reverse('admin:signage_color_change', args=[self.color.pk])
        response = self.client.post(change_url, {'label': 'coucou'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Color.objects.get(pk=self.color.pk).label, 'coucou')
        self.assertEqual(response.url, '/admin/signage/color/')


class DirectionAdminNoBypassTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.direction = BladeDirectionFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_direction_changelist(self):
        changelist_url = reverse('admin:signage_direction_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Direction.objects.get(pk=self.direction.pk).label)

    def test_direction_can_be_change(self):
        change_url = reverse('admin:signage_direction_change', args=[self.direction.pk])
        response = self.client.post(change_url, {'label': 'coucou'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Direction.objects.get(pk=self.direction.pk).label, 'coucou')
        self.assertEqual(response.url, '/admin/signage/direction/')


class BladeTypeAdminNoBypassTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(is_staff=True)
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            cls.user.user_permissions.add(perm)
        p = cls.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        cls.bladetype = BladeTypeFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(self.user)

    def test_bladetype_changelist(self):
        changelist_url = reverse('admin:signage_bladetype_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, BladeType.objects.get(pk=self.bladetype.pk).label)

    def test_bladetype_can_be_change(self):
        change_url = reverse('admin:signage_bladetype_change', args=[self.bladetype.pk])
        response = self.client.post(change_url, {'label': 'coucou', 'structure': StructureFactory.create().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BladeType.objects.get(pk=self.bladetype.pk).label, 'coucou')
        self.assertEqual(response.url, '/admin/signage/bladetype/')

    def test_bladetype_change_not_same_structure(self):
        structure = StructureFactory(name="Other")
        bladetype = BladeTypeFactory.create(structure=structure)
        change_url = reverse('admin:signage_bladetype_change', args=[bladetype.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BladeType.objects.get(pk=self.bladetype.pk).label, self.bladetype.label)
        self.assertEqual(response.url, '/admin/')


class BladeTypeAdminTest(BladeTypeAdminNoBypassTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        perm_bypass = Permission.objects.get(codename='can_bypass_structure')
        cls.user.user_permissions.add(perm_bypass)

    def test_bladetype_change_not_same_structure(self):
        structure = StructureFactory(name="Other")
        bladetype = BladeTypeFactory.create(structure=structure)
        change_url = reverse('admin:signage_bladetype_change', args=[bladetype.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="structure" ')


class SealingAdminTest(SealingAdminNoBypassTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        perm_bypass = Permission.objects.get(codename='can_bypass_structure')
        cls.user.user_permissions.add(perm_bypass)

    def test_sealing_change_not_same_structure(self):
        structure = StructureFactory(name="Other")
        sealing = SealingFactory.create(structure=structure)
        change_url = reverse('admin:signage_sealing_change', args=[sealing.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="structure" ')


class SignageTypeAdminTest(SignageTypeAdminNoBypassTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        perm_bypass = Permission.objects.get(codename='can_bypass_structure')
        cls.user.user_permissions.add(perm_bypass)

    def test_signage_type_change_not_same_structure(self):
        structure = StructureFactory(name="Other")
        signagetype = SignageTypeFactory.create(structure=structure)
        change_url = reverse('admin:signage_signagetype_change', args=[signagetype.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="structure" ')


class SignageConditionAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        structure = StructureFactory(name="First structure")
        cls.second_structure = StructureFactory(name="Second structure")

        # User without "can_bypass_structure" permission

        cls.user_withoutperm = UserFactory.create(is_staff=True)
        for perm in Permission.objects.exclude(codename='can_bypass_structure'):
            cls.user_withoutperm.user_permissions.add(perm)

        p = cls.user_withoutperm.profile
        p.structure = structure
        p.save()

        # User with "can_bypass_structure" permission
        cls.user_perm = UserFactory.create(is_staff=True)
        for perm in Permission.objects.all():
            cls.user_perm.user_permissions.add(perm)
        p = cls.user_perm.profile
        p.structure = structure
        p.save()
        cls.signage_condition = SignageConditionFactory.create(structure=structure)
        SignageConditionFactory.create(structure=cls.second_structure)

    def test_get_queryset_signage_conditions_withpermission(self):
        self.client.force_login(self.user_perm)
        change_url = reverse('admin:signage_signagecondition_change', args=[self.signage_condition.pk])
        response = self.client.get(change_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SignageCondition.objects.count(), 2)

    def test_get_queryset_signage_conditions_withoutpermission(self):
        self.client.force_login(self.user_withoutperm)
        change_url = reverse('admin:signage_signagecondition_change', args=[self.signage_condition.pk])
        response = self.client.get(change_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SignageCondition.objects.filter(structure=self.second_structure.pk).count(), 1)

    def test_formfield_for_foreignkey_signage_conditions_withpermission(self):
        self.client.force_login(self.user_perm)
        structure = StructureFactory(name="Other structure")
        signagecondition = SignageConditionFactory.create(structure=structure)
        change_url = reverse('admin:signage_signagecondition_change', args=[signagecondition.pk])
        response = self.client.get(change_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="structure" ')
        self.assertContains(response, '<input type="text" name="label" value="{}" class="vTextField" maxlength="250" required id="id_label">'.format(signagecondition.label))

    def test_formfield_for_foreignkey_signage_conditions_withoutpermission(self):
        self.client.force_login(self.user_withoutperm)
        structure = StructureFactory(name="Other structure")
        signagecondition = SignageConditionFactory.create(structure=structure)
        change_url = reverse('admin:signage_signagecondition_change', args=[signagecondition.pk])
        response = self.client.get(change_url)

        self.assertEqual(response.status_code, 302)

    def test_save_model_signage_conditions_withpermission(self):
        self.client.force_login(self.user_perm)
        change_url = reverse('admin:signage_signagecondition_add')
        response = self.client.post(change_url, data={
            "structure": StructureFactory(name="Other structure").pk,
            "label": "New condition"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SignageCondition.objects.count(), 3)

    def test_save_model_signage_conditions_withoutpermission(self):
        self.client.force_login(self.user_withoutperm)
        change_url = reverse('admin:signage_signagecondition_add')
        response = self.client.post(change_url, data={
            "structure": StructureFactory(name="Other structure").pk,
            "label": "New condition"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SignageCondition.objects.count(), 3)

    def test_get_list_display_signage_conditions_withpermission(self):
        self.client.force_login(self.user_perm)
        change_url = reverse('admin:signage_signagecondition_changelist')
        response = self.client.get(change_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="/admin/signage/signagecondition/{}/change/">{}</a>'.format(self.signage_condition.pk, self.signage_condition.label))

    def test_get_list_display_signage_conditions_withoutpermission(self):
        self.client.force_login(self.user_withoutperm)
        change_url = reverse('admin:signage_signagecondition_changelist')
        response = self.client.get(change_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="/admin/signage/signagecondition/{}/change/">{}</a>'.format(self.signage_condition.pk, self.signage_condition.label))
