from django.test import TestCase

from caminae.core.models import TopologyMixin
from caminae.core.factories import PathFactory, TopologyMixinFactory
from caminae.core.widgets import TopologyWidget


class WidgetsTest(TestCase):
    def test_serialize(self):
        topology = TopologyMixinFactory.create()
        self.assertEqual(len(topology.paths.all()), 1)
        pathpk = topology.paths.all()[0].pk
        kindpk = topology.kind.pk
        widget = TopologyWidget()
        fieldvalue = widget.serialize(topology)
        self.assertEqual(fieldvalue, '{"paths": [{"path": %s, "end": 1.0, "start": 0.0}], "kind": %s, "offset": 1}' % (pathpk, kindpk))

    def test_deserialize(self):
        path = PathFactory.create()
        widget = TopologyWidget()
        topology = widget.deserialize('{"paths": [{"path": %s, "end": 1.0, "start": 0.0}], "offset": 1}' % (path.pk))
        self.assertEqual(topology.offset, 1)
        self.assertEqual(topology.kind, TopologyMixin.get_kind())
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(topology.aggregations.all()[0].path, path)
        self.assertEqual(topology.aggregations.all()[0].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[0].end_position, 1.0)
