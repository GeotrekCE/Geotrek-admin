from django.test import TestCase
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory

from geotrek.tourism.models import InformationDesk
from geotrek.tourism.tests.factories import InformationDeskTypeFactory


class InformationDeskTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.type_information_desk = InformationDeskTypeFactory(label="Office")

    def setUp(self):
        self.client.force_login(self.user)

    def test_creation(self):
        post_data = {
            "name_en": "Office en",
            "name_fr": "Office fr",
            "type": self.type_information_desk.pk,
            "geom": "SRID=2154;POINT(5.1 6.6)",
            "common-attachment-content_type-object_id-TOTAL_FORMS": 0,
            "common-attachment-content_type-object_id-INITIAL_FORMS": 0,
            "common-attachment-content_type-object_id-MIN_NUM_FORMS": 0,
            "common-attachment-content_type-object_id-MAX_NUM_FORMS": 1000,
        }

        self.client.post(reverse("admin:tourism_informationdesk_add"), post_data)
        self.assertEqual(InformationDesk.objects.get().name_en, "Office en")
