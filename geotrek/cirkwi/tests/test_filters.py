from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase

from geotrek.common.tests.factories import TargetPortalFactory

from geotrek.authent.tests.factories import StructureFactory
from geotrek.core.tests.factories import PathFactory

from geotrek.trekking.tests.factories import POIFactory, TrekFactory
from geotrek.cirkwi.filters import CirkwiPOIFilterSet, CirkwiTrekFilterSet


class CirkwiFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.path = PathFactory()
            cls.poi = POIFactory.create(paths=[(cls.path, 0, 1)])
            cls.trek = TrekFactory.create(paths=[(cls.path, 0, 1)])
        else:
            cls.poi = POIFactory.create(geom=Point(0, 0))
            cls.trek = TrekFactory.create(geom=LineString((0, 0), (5, 5)))

    def test_trek_filters_structures(self):
        other_structure = StructureFactory.create()
        qs = CirkwiTrekFilterSet(data={"structures": f'{self.trek.structure.pk}'}).qs
        self.assertEqual(qs.count(), 1)
        qs = CirkwiTrekFilterSet(data={"structures": f'{other_structure.pk}'}).qs
        self.assertEqual(qs.count(), 0)
        qs = CirkwiTrekFilterSet(data={"structures": '0'}).qs
        self.assertEqual(qs.count(), 1)
        qs = CirkwiTrekFilterSet(data={"structures": 'a'}).qs
        self.assertEqual(qs.count(), 1)

    def test_trek_filters_portals(self):
        portal = TargetPortalFactory.create()
        self.trek.portal.add(portal)
        other_portal = TargetPortalFactory.create()
        qs = CirkwiTrekFilterSet(data={"portals": f'{portal.pk}'}).qs
        self.assertEqual(qs.count(), 1)
        qs = CirkwiTrekFilterSet(data={"portals": f'{other_portal.pk}'}).qs
        self.assertEqual(qs.count(), 0)
        qs = CirkwiTrekFilterSet(data={"portals": '0'}).qs
        self.assertEqual(qs.count(), 1)
        qs = CirkwiTrekFilterSet(data={"portals": 'a'}).qs
        self.assertEqual(qs.count(), 1)

    def test_poi_filters_structures(self):
        other_structure = StructureFactory.create()
        qs = CirkwiPOIFilterSet(data={"structures": f'{self.poi.structure.pk}'}).qs
        self.assertEqual(qs.count(), 1)
        qs = CirkwiPOIFilterSet(data={"structures": f'{other_structure.pk}'}).qs
        self.assertEqual(qs.count(), 0)
        qs = CirkwiPOIFilterSet(data={"structures": '0'}).qs
        self.assertEqual(qs.count(), 1)
        qs = CirkwiPOIFilterSet(data={"structures": 'a'}).qs
        self.assertEqual(qs.count(), 1)
