# -*- coding: utf-8 -*-
from django.test import TestCase
from unittest import skipIf

from django.conf import settings

from geotrek.core.factories import PathFactory
from geotrek.signage.factories import SignageFactory, SealingFactory, BladeTypeFactory, BladeFactory
from geotrek.infrastructure.factories import InfrastructureFactory
from django.contrib.gis.geos import LineString, Point


class SignageModelTest(TestCase):
    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_gps_value_all_cases(self):
        path = PathFactory.create(geom=LineString((-4, -4), (4, 4), srid=4326))
        signage_N_E = SignageFactory.create(no_path=True)
        signage_S_W = SignageFactory.create(no_path=True)
        signage_N_E.add_path(path, start=1, end=1)
        signage_S_W.add_path(path, start=0, end=0)
        self.assertEqual(signage_N_E.gps_value, u'4.0°N, 4.0°E')
        self.assertEqual(signage_S_W.gps_value, u'4.0°S, 4.0°W')

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_gps_value_all_cases_nds(self):
        signage_N_E = SignageFactory.create(geom=Point(4, 4, srid=4326))
        signage_S_W = SignageFactory.create(geom=Point(-4, -4, srid=4326))
        self.assertEqual(signage_N_E.gps_value, u'4.0°N, 4.0°E')
        self.assertEqual(signage_S_W.gps_value, u'4.0°S, 4.0°W')


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
        with self.assertRaises(ValueError) as e:
            blade.set_topology(infra)
        self.assertEqual(e.exception.message, "Expecting a signage")
