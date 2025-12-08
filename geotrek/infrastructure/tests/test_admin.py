import os

from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory, UserFactory

from geotrek.authent.tests.factories import StructureFactory
from geotrek.infrastructure.models import (
    InfrastructureCondition,
    InfrastructureMaintenanceDifficultyLevel,
    InfrastructureType,
    InfrastructureUsageDifficultyLevel,
)
from geotrek.infrastructure.tests.factories import (
    InfrastructureConditionFactory,
    InfrastructureMaintenanceDifficultyLevelFactory,
    InfrastructureTypeFactory,
    InfrastructureUsageDifficultyLevelFactory,
)


class InfrastructureTypeAdminNoBypassTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(is_staff=True)
        p = cls.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        cls.infra = InfrastructureTypeFactory.create(structure=structure)
        cls.user.user_permissions.add(Permission.objects.get(codename="add_draft_path"))
        for perm in Permission.objects.exclude(codename="can_bypass_structure"):
            cls.user.user_permissions.add(perm)

    def setUp(self):
        self.client.force_login(self.user)

    def test_infrastructure_type_changelist(self):
        changelist_url = reverse("admin:infrastructure_infrastructuretype_changelist")
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, InfrastructureType.objects.get(pk=self.infra.pk).label
        )

    def test_infrastructure_type_can_be_change(self):
        change_url = reverse(
            "admin:infrastructure_infrastructuretype_change", args=[self.infra.pk]
        )
        response = self.client.post(
            change_url,
            {
                "label": "coucou",
                "type": "A",
                "pictogram": os.path.join(
                    settings.MEDIA_URL, self.infra.pictogram.name
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            InfrastructureType.objects.get(pk=self.infra.pk).label, "coucou"
        )
        self.assertEqual(response.url, "/admin/infrastructure/infrastructuretype/")

    def test_infrastructure_type_cannot_be_change_not_same_structure(self):
        structure = StructureFactory(name="Other")
        infra = InfrastructureTypeFactory.create(structure=structure)
        change_url = reverse(
            "admin:infrastructure_infrastructuretype_change", args=[infra.pk]
        )
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            InfrastructureType.objects.get(pk=self.infra.pk).label, self.infra.label
        )
        self.assertEqual(response.url, "/admin/")


class InfrastructureConditionAdminNoBypassTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(is_staff=True)
        p = cls.user.profile
        structure = StructureFactory(name="This")
        p.structure = structure
        p.save()
        cls.user.user_permissions.add(Permission.objects.get(codename="add_draft_path"))
        for perm in Permission.objects.exclude(codename="can_bypass_structure"):
            cls.user.user_permissions.add(perm)
        cls.infra = InfrastructureConditionFactory.create(structure=structure)

    def setUp(self):
        self.client.force_login(self.user)

    def test_infrastructure_condition_changelist(self):
        changelist_url = reverse(
            "admin:infrastructure_infrastructurecondition_changelist"
        )
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, InfrastructureCondition.objects.get(pk=self.infra.pk).label
        )

    def test_infrastructure_condition_can_be_change(self):
        change_url = reverse(
            "admin:infrastructure_infrastructurecondition_change", args=[self.infra.pk]
        )
        response = self.client.post(
            change_url, {"label": "coucou", "structure": StructureFactory.create().pk}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            InfrastructureCondition.objects.get(pk=self.infra.pk).label, "coucou"
        )
        self.assertEqual(response.url, "/admin/infrastructure/infrastructurecondition/")

    def test_infrastructure_condition_cannot_be_change_not_same_structure(self):
        structure = StructureFactory(name="Other")
        infra = InfrastructureConditionFactory.create(structure=structure)
        change_url = reverse(
            "admin:infrastructure_infrastructurecondition_change", args=[infra.pk]
        )
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            InfrastructureCondition.objects.get(pk=self.infra.pk).label,
            self.infra.label,
        )
        self.assertEqual(response.url, "/admin/")


class InfrastructureTypeAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory()
        cls.infrastructure_type = InfrastructureTypeFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_infrastructure_type_can_be_change(self):
        change_url = reverse(
            "admin:infrastructure_infrastructuretype_change",
            args=[self.infrastructure_type.pk],
        )
        response = self.client.post(
            change_url,
            {
                "label": "coucou",
                "type": "A",
                "pictogram": os.path.join(
                    settings.MEDIA_URL, self.infrastructure_type.pictogram.name
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            InfrastructureType.objects.get(pk=self.infrastructure_type.pk).label,
            "coucou",
        )
        self.assertEqual(response.url, "/admin/infrastructure/infrastructuretype/")

    def test_infrastructure_type_changelist(self):
        changelist_url = reverse("admin:infrastructure_infrastructuretype_changelist")
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            InfrastructureType.objects.get(pk=self.infrastructure_type.pk).label,
        )

    def test_infrastructure_type_search(self):
        """Test search in infrastructure type list"""
        changelist_url = (
            reverse("admin:infrastructure_infrastructuretype_changelist") + "?q=coucou"
        )
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)


class InfrastructureConditionAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory()
        cls.infrastructure_condition = InfrastructureConditionFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_infrastructure_condition_can_be_change(self):
        change_url = reverse(
            "admin:infrastructure_infrastructurecondition_change",
            args=[self.infrastructure_condition.pk],
        )
        response = self.client.post(
            change_url, {"label": "coucou", "structure": StructureFactory.create().pk}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            InfrastructureCondition.objects.get(
                pk=self.infrastructure_condition.pk
            ).label,
            "coucou",
        )
        self.assertEqual(response.url, "/admin/infrastructure/infrastructurecondition/")

    def test_infrastructure_condition_changelist(self):
        changelist_url = reverse(
            "admin:infrastructure_infrastructurecondition_changelist"
        )
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            InfrastructureCondition.objects.get(
                pk=self.infrastructure_condition.pk
            ).label,
        )


class InfrastructureUsageDifficultyAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory()
        cls.level = InfrastructureUsageDifficultyLevelFactory(
            label="Medium", structure=StructureFactory(name="Ecorp")
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_infrastructure_usage_difficulty_level_display_string(self):
        """Test string formatting for usage difficulty levels"""
        self.assertEqual(str(self.level), "Medium (Ecorp)")

    def test_infrastructure_usage_difficulty_can_be_changed(self):
        """Test admin update view for usage difficulty levels"""
        change_url = reverse(
            "admin:infrastructure_infrastructureusagedifficultylevel_change",
            args=[self.level.pk],
        )
        response = self.client.post(change_url, {"label": "Easy"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            InfrastructureUsageDifficultyLevel.objects.get(pk=self.level.pk).label,
            "Easy",
        )
        self.assertEqual(
            response.url, "/admin/infrastructure/infrastructureusagedifficultylevel/"
        )

    def test_infrastructurecondition_changelist(self):
        """Test admin list view for usage difficulty levels"""
        changelist_url = reverse(
            "admin:infrastructure_infrastructureusagedifficultylevel_changelist"
        )
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            InfrastructureUsageDifficultyLevel.objects.get(pk=self.level.pk).label,
        )


class InfrastructureMaintenanceDifficultyAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory()
        cls.level = InfrastructureMaintenanceDifficultyLevelFactory(
            label="Medium", structure=StructureFactory(name="Ecorp")
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_infrastructure_maintenance_difficulty_level_display_string(self):
        """Test string formatting for maintenance difficulty levels"""
        self.assertEqual(str(self.level), "Medium (Ecorp)")

    def test_infrastructure_maintenance_difficulty_can_be_changed(self):
        """Test admin update view for maintenance difficulty levels"""
        change_url = reverse(
            "admin:infrastructure_infrastructuremaintenancedifficultylevel_change",
            args=[self.level.pk],
        )
        response = self.client.post(change_url, {"label": "Easy"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            InfrastructureMaintenanceDifficultyLevel.objects.get(
                pk=self.level.pk
            ).label,
            "Easy",
        )
        self.assertEqual(
            response.url,
            "/admin/infrastructure/infrastructuremaintenancedifficultylevel/",
        )

    def test_infrastructurecondition_maintenance_difficulty_changelist(self):
        """Test list view for maintenance difficulty levels"""
        changelist_url = reverse(
            "admin:infrastructure_infrastructuremaintenancedifficultylevel_changelist"
        )
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            InfrastructureMaintenanceDifficultyLevel.objects.get(
                pk=self.level.pk
            ).label,
        )
