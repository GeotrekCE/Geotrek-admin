from django.test import TestCase

from geotrek.common.tests import TranslationResetMixin
from geotrek.diving.models import Dive
from geotrek.diving.factories import DiveFactory, DivingManagerFactory, PracticeFactory, LevelFactory

from mapentity.factories import SuperUserFactory


class DiveTest(TranslationResetMixin, TestCase):

    def test_levels_display(self):
        """Test if levels_display works"""
        l1 = LevelFactory.create()
        l2 = LevelFactory.create()
        d = DiveFactory()
        d.levels.add(l1)
        d.levels.add(l2)
        self.assertEquals(d.levels_display, "{0}, {1}".format(l1, l2))
