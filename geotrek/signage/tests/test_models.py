from django.test import TestCase
from unittest import skipIf

from django.conf import settings

from geotrek.core.factories import PathFactory
from geotrek.signage.factories import SignageFactory, SealingFactory, BladeTypeFactory, BladeFactory
from geotrek.infrastructure.factories import InfrastructureFactory
from django.contrib.gis.geos import LineString, Point


class SignageModelTest(TestCase):
    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_gps_value_mercator_case(self):
        path = PathFactory.create(geom=LineString((-4, -4), (4, 4), srid=4326))
        signage_N_E = SignageFactory.create(no_path=True)
        signage_S_W = SignageFactory.create(no_path=True)
        signage_N_E.add_path(path, start=1, end=1)
        signage_S_W.add_path(path, start=0, end=0)
        self.assertEqual(signage_N_E.gps_value, '4°00\'00" N / 4°00\'00" E (WGS 84 / Pseudo-Mercator)')
        self.assertEqual(signage_S_W.gps_value, '4°00\'00" S / 4°00\'00" W (WGS 84 / Pseudo-Mercator)')

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_gps_value_other_cases(self):
        path = PathFactory.create(geom=LineString((-200000, -400000), (200000, 400000), srid=32631))
        settings.DISPLAY_SRID = 32631
        signage_N_E = SignageFactory.create(no_path=True)
        signage_S_W = SignageFactory.create(no_path=True)
        signage_N_E.add_path(path, start=1, end=1)
        signage_S_W.add_path(path, start=0, end=0)
        self.assertEqual(signage_N_E.gps_value, 'X: 200000 / Y: 400000 (WGS 84 / UTM zone 31N)')
        self.assertEqual(signage_S_W.gps_value, 'X: -200000 / Y: -400000 (WGS 84 / UTM zone 31N)')

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_gps_value_mercator_case_nds(self):
        signage_N_E = SignageFactory.create(geom=Point(4, 4, srid=4326))
        signage_S_W = SignageFactory.create(geom=Point(-4, -4, srid=4326))
        self.assertEqual(signage_N_E.gps_value, '4°00\'00" N / 4°00\'00" E (WGS 84 / Pseudo-Mercator)')
        self.assertEqual(signage_S_W.gps_value, '4°00\'00" S / 4°00\'00" W (WGS 84 / Pseudo-Mercator)')

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_gps_value_other_cases_nds(self):
        signage_N_E = SignageFactory.create(geom=Point(200000, 400000, srid=32631))
        signage_S_W = SignageFactory.create(geom=Point(-200000, -400000, srid=32631))
        self.assertEqual(signage_N_E.gps_value, 'X: 200000 / Y: 400000 (WGS 84 / UTM zone 31N)')
        self.assertEqual(signage_S_W.gps_value, 'X: -200000 / Y: -400000 (WGS 84 / UTM zone 31N)')


class SealingModelTest(TestCase):
    def test_sealing_value(self):
        sealing = SealingFactory.create(label='sealing_1', structure=None)
        self.assertEqual(str(sealing), 'sealing_1')


class BladeTypeModelTest(TestCase):
    def test_bladetype_value(self):
        type = BladeTypeFactory.create(label='type_1', structure=None)
        self.assertEqual(str(type), 'type_1')


class BladeModelTest(TestCase):
    def test_set_topology_other_error(self):
        blade = BladeFactory.create()
        infra = InfrastructureFactory.create()
        with self.assertRaisesRegexp(ValueError, "Expecting a signage"):
            blade.set_topology(infra)
