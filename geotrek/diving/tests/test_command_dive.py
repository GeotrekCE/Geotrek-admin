import os
import mock
import sys
from StringIO import StringIO

from django.contrib.gis.geos.error import GEOSException
from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError

from geotrek.common.utils import almostequal
from geotrek.core.factories import PathFactory
from geotrek.diving.factories import DiveFactory
from geotrek.diving.models import Dive
from geotrek.authent.factories import StructureFactory


class DiveCommandTest(TestCase):
    """
    There are 2 dives in the file dive.shp

    name        eid         depth

    coucou      eid1        2010
    name        eid2        5
    """
    def test_load_dive_eid(self):
        output = StringIO()
        structure = StructureFactory.create(name='structure')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'dive.shp')
        DiveFactory.create(name='name', eid='eid1', depth=10)
        call_command('loaddive', filename, name_field='name', depth_field='depth',  eid_field='eid',
                     practice_default='Practice', structure_default='structure', verbosity=2, stdout=output)
        self.assertIn('Dives will be linked to %s' % structure, output.getvalue())
        self.assertIn('2 objects created.', output.getvalue())
        value = Dive.objects.filter(name='name')
        self.assertEquals(5, value[0].depth)    # The dive was updated because has the same eid (eid1)
        self.assertEquals(value.count(), 1)
        self.assertEquals(Dive.objects.count(), 2)
        self.assertTrue(almostequal(value[0].geom.x, -436345.7048306435))
        self.assertTrue(almostequal(value[0].geom.y, 1176487.7429172313))

    def test_load_dive_no_eid(self):
        output = StringIO()
        structure = StructureFactory.create(name='structure')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'dive.shp')
        DiveFactory.create(name='name', eid='eid1', depth=10)
        call_command('loaddive', filename, name_field='name', depth_field='depth', practice_default='Practice',
                     structure_default='structure', verbosity=2, stdout=output)
        self.assertIn('Dives will be linked to %s' % structure, output.getvalue())
        self.assertIn('2 objects created.', output.getvalue())
        value = Dive.objects.filter(name='name')
        self.assertEquals(10, value[0].depth)    # The dive was not updated
        self.assertEquals(value.count(), 2)
        self.assertEquals(Dive.objects.count(), 3)
        self.assertTrue(almostequal(value[1].geom.x, -436345.7048306435))
        self.assertTrue(almostequal(value[1].geom.y, 1176487.7429172313))
