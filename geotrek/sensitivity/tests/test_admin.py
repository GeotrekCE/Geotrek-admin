from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.urls import reverse
from mapentity.tests import UserFactory

from geotrek.sensitivity.admin import SpeciesAdmin
from geotrek.sensitivity.models import Species


class SpeciesAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.species_1 = Species.objects.create(
            name="Species 1", category=Species.CategoryChoices.SPECIES
        )
        cls.species_2 = Species.objects.create(
            name="Species 2", category=Species.CategoryChoices.REGULATORY
        )

    def setUp(self):
        self.site = AdminSite()
        self.admin = SpeciesAdmin(Species, self.site)

    def test_returns_only_species_category(self):
        queryset = self.admin.get_queryset(None)
        self.assertIn(self.species_1, queryset)
        self.assertNotIn(self.species_2, queryset)

    def test_returns_empty_queryset_if_no_species(self):
        Species.objects.all().delete()
        queryset = self.admin.get_queryset(None)
        self.assertEqual(queryset.count(), 0)


def test_admin_changelist(self):
    admin_user = UserFactory(is_staff=True, is_superuser=True)
    self.client.force_login(admin_user)

    url = reverse("admin:sensitivity_species_changelist")
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
