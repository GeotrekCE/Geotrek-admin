from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import LineString
from django.db import connections, DEFAULT_DB_ALIAS
from django.contrib.gis.geos import fromstr

class TriggerTest(TestCase):

    def test_smart_makeline(self):
        def smart_makeline(lines):
            conn = connections[DEFAULT_DB_ALIAS]
            cursor = conn.cursor()
            geoms = ["ST_GeomFromText('%s')" % l.wkt for l in lines]
            sql = "SELECT ST_AsText(ft_Smart_MakeLine(ARRAY[%s]));" % ','.join(geoms)
            cursor.execute(sql)
            result = cursor.fetchall()
            return fromstr(result[0][0])

        self.assertEqual(smart_makeline([
                            LineString((0,0),(1,0)),
                            LineString((2,0),(1,0)),
                            LineString((2,0),(2,4)),
                            LineString((2,4),(2,0)),
                            LineString((2,0),(3,0)),
                         ]),
                         LineString((0,0),(1,0),(2,0),(2,4),(2,0),(3,0)))