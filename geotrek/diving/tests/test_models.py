from django.test import TestCase

from geotrek.diving.models import Difficulty
from geotrek.diving.tests.factories import DiveFactory, LevelFactory


class DiveModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dive = DiveFactory.create(practice=None)

    def test_levels_display(self):
        """Test if levels_display works"""
        l1 = LevelFactory.create()
        l2 = LevelFactory.create()
        d = DiveFactory()
        d.levels.set([l1, l2])
        self.assertEqual(d.levels_display, f"{l1}, {l2}")

    def test_difficulty_save_auto_id(self):
        Difficulty.objects.create(id=10, name="Easy")
        d2 = Difficulty(name="Medium")
        d2.save()
        self.assertEqual(d2.id, 11)
