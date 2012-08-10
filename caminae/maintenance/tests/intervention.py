from django.test import TestCase
from django.contrib.gis.geos import Point

from caminae.maintenance.factories import InterventionFactory


class InterventionTest(TestCase):
    def test_init_point(self):
        intervention = InterventionFactory()
        intervention.initFromPoint(Point(15, 15))
