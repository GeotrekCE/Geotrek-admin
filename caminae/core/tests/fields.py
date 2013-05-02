from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import LineString
from django.conf import settings

from caminae.core.fields import SnappedLineStringField
from caminae.core.factories import PathFactory


class FieldsTest(TestCase):
    def test_snappedlinestring(self):
        f = SnappedLineStringField()

        self.assertRaises(ValidationError, f.clean, ('LINESTRING(0 0, 1 0)',))
        self.assertRaises(ValidationError, f.clean, ('{"geom": "LINESTRING(0 0, 1 0)"}',))
        self.assertRaises(ValidationError, f.clean, ('{"geom": "LINESTRING(0 0, 1 0)", "snap": [null]}',))
        self.assertRaises(ValidationError, f.clean, ('{"geom": "LINEPPRING(0 0, 1 0)", "snap": [null, null]}',))

        value = '{"geom": "LINESTRING(-0.77054223313507 -5.32573853776343,-0.168053647782867 -4.66595028627023)", "snap": [null, null]}'
        self.assertTrue(f.clean(value).equals_exact(LineString((100000, 100000), (200000, 200000), srid=settings.SRID), 0.1))

        path = PathFactory.create()
        value = '{"geom": "LINESTRING(-0.77054223313507 -5.32573853776343,-0.168053647782867 -4.66595028627023)", "snap": [null, %s]}' % path.pk
        self.assertTrue(f.clean(value).equals_exact(LineString((100000, 100000), (2, 2), srid=settings.SRID), 0.1))
