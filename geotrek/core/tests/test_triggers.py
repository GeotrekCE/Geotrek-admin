from django.test import TestCase
from django.contrib.gis.geos import LineString
from django.db import connections, DEFAULT_DB_ALIAS
from django.contrib.gis.geos import fromstr


class SmartMakelineTest(TestCase):

    def smart_makeline(self, lines):
        assert lines > 0
        if isinstance(lines[0], basestring):
            lines = ["ST_GeomFromText('%s')" % l for l in lines]
        else:
            lines = ["ST_GeomFromText('%s')" % l.wkt for l in lines]
        conn = connections[DEFAULT_DB_ALIAS]
        cursor = conn.cursor()
        sql = "SELECT ST_AsText(ft_Smart_MakeLine(ARRAY[%s]));" % ','.join(lines)
        cursor.execute(sql)
        result = cursor.fetchall()
        return fromstr(result[0][0])

    def test_smart_makeline(self):
        self.assertEqual(self.smart_makeline([
            LineString((0, 0), (1, 0)),
            LineString((2, 0), (1, 0)),
            LineString((2, 0), (2, 4)),
            LineString((2, 4), (2, 0)),
            LineString((2, 0), (3, 0))]), LineString((0, 0), (1, 0), (2, 0), (2, 4), (2, 0), (3, 0)))

    def test_makeline_with_actual_data(self):
        merged = self.smart_makeline([
            "LINESTRING(370833.911153277 4870490.01810693, 370818.507041415 4870524.70383139, 370813.434174652 4870531.90334984, 370789.94823107 4870554.22429755, 370789.81736043 4870559.14695767, 370793.911271824 4870564.25300474, 370828.975416977 4870574.54810465, 370868.85201029 4870572.85071902, 370895.861358561 4870566.70749199, 370971.504740896 4870544.67253984, 370998.517095177 4870550.56044067, 371009.641149807 4870561.15312567, 371012.769116307 4870570.74335641)",
            "LINESTRING(371012.769116307 4870570.74335641, 371062.718671741 4870543.02202545, 371077.498614357 4870531.58286525, 371106.169877355 4870503.55782705, 371141.783683489 4870459.87088356, 371146.823486222 4870440.24145094, 371144.066459758 4870428.91887793, 371140.299482569 4870425.49268807)",
            "LINESTRING(371140.299482569 4870425.49268807, 371134.666113917 4870423.91139172, 371126.060023413 4870425.4613796, 371101.747730562 4870442.12962888, 371077.099984334 4870453.00796507, 371066.323069209 4870455.02209549, 371061.786363116 4870453.35826919, 371032.133323583 4870403.05281244, 371018.683384518 4870370.87846625, 371009.813856395 4870355.60437563, 371000.012719456 4870342.60613872, 370995.164088116 4870339.46186412, 370995.131678931 4870339.45547179)"
        ])
        self.assertEqual(merged.geom_type, 'LineString')

    def test_smart_makeline_unordered(self):
        merged = self.smart_makeline([
            LineString((2, 0), (4, 0)),
            LineString((4, 0), (8, 0)),
            LineString((8, 0), (9, 0)),
            LineString((9, 0), (10, 0)),
            LineString((9, 0), (8, 0)),
            LineString((10, 0), (9, 0)),
            LineString((8, 0), (4, 0)),
            LineString((4, 0), (2, 0)),
        ])
        self.assertEqual(merged,
                         LineString((2, 0), (4, 0), (8, 0), (9, 0), (10, 0), (9, 0), (8, 0), (4, 0), (2, 0)),
                         merged.coords)
