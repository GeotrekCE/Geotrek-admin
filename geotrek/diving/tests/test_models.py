from geotrek.common.tests import TranslationResetMixin

from geotrek.diving.factories import DiveFactory, LevelFactory
from geotrek.diving.factories import PracticeFactory

from django.test import TestCase, override_settings


class DiveModelTest(TranslationResetMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super(DiveModelTest, cls).setUpClass()
        cls.dive = DiveFactory.create(practice=None)

    def test_levels_display(self):
        """Test if levels_display works"""
        l1 = LevelFactory.create()
        l2 = LevelFactory.create()
        d = DiveFactory()
        d.levels.set([l1, l2])
        self.assertEquals(d.levels_display, "{0}, {1}".format(l1, l2))

    def test_rando_url(self):
        self.assertEqual(self.dive.rando_url, "dive/dive/")

    @override_settings(SPLIT_DIVES_CATEGORIES_BY_PRACTICE=True)
    def test_rando_url_split_by_category_no_practice(self):
        self.assertEqual(self.dive.rando_url, "dive/dive/")

    @override_settings(SPLIT_DIVES_CATEGORIES_BY_PRACTICE=True)
    def test_rando_url_split_by_category(self):
        practice = PracticeFactory.create(name="special")
        dive = DiveFactory.create()
        dive.practice = practice
        dive.save()
        self.assertEqual(dive.rando_url, "special/dive/")

    def test_prefixed_category_id(self):
        self.assertEqual(self.dive.prefixed_category_id, "D")

    @override_settings(SPLIT_DIVES_CATEGORIES_BY_PRACTICE=True)
    def test_prefixed_category_id_no_practice(self):
        self.assertEqual(self.dive.prefixed_category_id, "D")

    @override_settings(SPLIT_DIVES_CATEGORIES_BY_PRACTICE=True)
    def test_prefixed_category_id_with_practice(self):
        practice = PracticeFactory.create(name="special")
        dive = DiveFactory.create()
        dive.practice = practice
        dive.save()
        self.assertEqual(dive.prefixed_category_id, "D%s" % practice.id)
