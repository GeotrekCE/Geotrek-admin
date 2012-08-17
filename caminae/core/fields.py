import floppyforms as forms

from .widgets import TopologyWidget, PointLineTopologyWidget


class TopologyField(forms.CharField):
    widget = TopologyWidget


class PointLineTopologyField(TopologyField):
    widget = PointLineTopologyWidget
