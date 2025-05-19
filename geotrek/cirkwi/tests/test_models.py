from django.test import TestCase

from geotrek.cirkwi.models import CirkwiLocomotion, CirkwiPOICategory, CirkwiTag


class CirkwiModelTest(TestCase):
    def test_cirkwitag_value(self):
        tag = CirkwiTag.objects.create(name="tag_1", eid=0)
        self.assertEqual(str(tag), "tag_1")

    def test_cirkwilocomotion_value(self):
        loco = CirkwiLocomotion.objects.create(name="loco_1", eid=0)
        self.assertEqual(str(loco), "loco_1")

    def test_cirkwipoicategory_value(self):
        poicategory = CirkwiPOICategory.objects.create(name="poicategory_1", eid=0)
        self.assertEqual(str(poicategory), "poicategory_1")
