from django.test import TestCase
from django.urls import reverse

from geotrek.tourism.models import InformationDesk
from geotrek.tourism.tests.factories import InformationDeskTypeFactory
from mapentity.tests.factories import SuperUserFactory


class InformationDeskTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.type_information_desk = InformationDeskTypeFactory(label="Office")

    def setUp(self):
        self.client.force_login(self.user)

    def get_csrf_token(self, response):
        csrf = 'name="csrfmiddlewaretoken" value="'
        start = response.content.decode().find(csrf) + len(csrf)
        end = response.content.decode().find('"', start)
        return response.content[start:end]

    def test_creation(self):
        response = self.client.get(reverse('admin:tourism_informationdesk_add'))
        csrf = self.get_csrf_token(response)
        post_data = {'id': 1,
                     'name_en': 'Office en',
                     'name_fr': 'Office fr',
                     'type': self.type_information_desk.pk,
                     'csrfmiddlewaretoken': csrf,
                     'geom': 'SRID=2154;POINT(5.1 6.6)'}

        self.client.post(reverse('admin:tourism_informationdesk_add'), post_data)
        self.assertEqual(InformationDesk.objects.get().name_en, 'Office en')
