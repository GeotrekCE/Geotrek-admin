import floppyforms as forms

from .widgets import TopologyWidget, PointLineTopologyWidget


class TopologyField(forms.gis.GeometryField):
    widget = TopologyWidget


class PointLineTopologyField(TopologyField):
    widget = PointLineTopologyWidget
