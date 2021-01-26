from django.test import TestCase
from django.urls import reverse

from mapentity.factories import SuperUserFactory

from geotrek.zoning.factories import CityFactory, DistrictFactory, RestrictedAreaFactory
from geotrek.zoning.models import City, District, RestrictedArea


class ZoningAdminTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ZoningAdminTest, cls).setUpClass()
        cls.user = SuperUserFactory.create(password='booh')

    def login(self):
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def test_publish_city(self):
        self.login()
        CityFactory.create(published=True)
        CityFactory.create(published=False)
        data = {'action': 'publish', '_selected_action': City.objects.all().values_list('pk', flat=True)}
        self.client.post(reverse("admin:zoning_city_changelist"), data, follow=True)
        self.assertEqual(City.objects.filter(published=False).count(), 0)

    def test_unpublish_city(self):
        self.login()
        CityFactory.create(published=True)
        CityFactory.create(published=False)
        data = {'action': 'unpublish', '_selected_action': City.objects.all().values_list('pk', flat=True)}
        self.client.post(reverse("admin:zoning_city_changelist"), data, follow=True)
        self.assertEqual(City.objects.filter(published=False).count(), 2)

    def test_publish_district(self):
        self.login()
        DistrictFactory.create(published=True)
        DistrictFactory.create(published=False)
        data = {'action': 'publish', '_selected_action': District.objects.all().values_list('pk', flat=True)}
        self.client.post(reverse("admin:zoning_district_changelist"), data, follow=True)
        self.assertEqual(City.objects.filter(published=False).count(), 0)

    def test_unpublish_district(self):
        self.login()
        DistrictFactory.create(published=True)
        DistrictFactory.create(published=False)
        data = {'action': 'unpublish', '_selected_action': District.objects.all().values_list('pk', flat=True)}
        self.client.post(reverse("admin:zoning_district_changelist"), data, follow=True)
        self.assertEqual(District.objects.filter(published=False).count(), 2)

    def test_publish_area(self):
        self.login()
        RestrictedAreaFactory.create(published=True)
        RestrictedAreaFactory.create(published=False)
        data = {'action': 'publish', '_selected_action': RestrictedArea.objects.all().values_list('pk', flat=True)}
        self.client.post(reverse("admin:zoning_restrictedarea_changelist"), data, follow=True)
        self.assertEqual(RestrictedArea.objects.filter(published=False).count(), 0)

    def test_unpublish_area(self):
        self.login()
        RestrictedAreaFactory.create(published=True)
        RestrictedAreaFactory.create(published=False)
        data = {'action': 'unpublish', '_selected_action': RestrictedArea.objects.all().values_list('pk', flat=True)}
        self.client.post(reverse("admin:zoning_restrictedarea_changelist"), data, follow=True)
        self.assertEqual(RestrictedArea.objects.filter(published=False).count(), 2)
