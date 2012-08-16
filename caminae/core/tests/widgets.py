from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import LineString, Polygon, MultiPolygon
from django.db import connections, DEFAULT_DB_ALIAS

from caminae.core.factories import PathFactory, TopologyMixinFactory, TopologyMixinKindFactory
from caminae.core.models import Path
from caminae.core.widgets import TopologyWidget


class WidgetsTest(TestCase):
    def test_serialize(self):
        topology = TopologyMixinFactory.create()
        widget = TopologyWidget()
        fieldvalue = widget.serialize(topology)
        self.assertEqual(fieldvalue, '{"paths": [{"path": 19, "end": 1.0, "start": 0.0}], "kind": %s, "offset": 1}' % topology.kind.pk)

    def test_deserialize(self):
        path = PathFactory.create()
        kind = TopologyMixinKindFactory.create()
        widget = TopologyWidget()
        topology = widget.deserialize('{"paths": [{"path": %s, "end": 1.0, "start": 0.0}], "kind": %s, "offset": 1}' % (path.pk, kind.pk))
        self.assertEqual(topology.offset, 1)
        self.assertEqual(topology.kind, kind)
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(topology.paths.all()[0].path, path)
        self.assertEqual(topology.paths.all()[0].start_position, 0.0)
        self.assertEqual(topology.paths.all()[0].end_position, 1.0)
