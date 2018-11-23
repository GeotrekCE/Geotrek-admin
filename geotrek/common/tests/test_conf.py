# -*- encoding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from geotrek.common.utils.signals import check_srid_has_meter_unit


class StartupCheckTest(TestCase):
    def test_error_is_raised_if_srid_is_not_meters(self):
        if hasattr(check_srid_has_meter_unit, '_checked'):
            delattr(check_srid_has_meter_unit, '_checked')
        with self.settings(SRID=4326):
            self.assertRaises(ImproperlyConfigured, check_srid_has_meter_unit)

    def test_error_is_not_raised_if_srid_is_meters(self):
        if hasattr(check_srid_has_meter_unit, '_checked'):
            delattr(check_srid_has_meter_unit, '_checked')
        try:
            with self.settings(SRID=2154):
                command = check_srid_has_meter_unit
                self.assertTrue(command)
        except ImproperlyConfigured:
            self.fail('check_srid_has_meter_unit raised ImproperlyConfigured unexpectedly!')
