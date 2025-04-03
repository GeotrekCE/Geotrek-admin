from django.test import TestCase

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
        self.assertEqual(d.levels_display, "{0}, {1}".format(l1, l2))
