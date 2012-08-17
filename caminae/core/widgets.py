from django.conf import settings
from django.utils import simplejson
import floppyforms as forms

from caminae.common.utils import wkt_to_geom
from .models import Path, TopologyMixin, TopologyMixinKind, PathAggregation
from .factories import TopologyMixinFactory


class LeafletMapWidget(forms.gis.BaseGeometryWidget):
    template_name = 'core/formfieldmap_fragment.html'
    display_wkt = settings.DEBUG

    def value_from_datadict(self, data, files, name):
        wkt = super(LeafletMapWidget, self).value_from_datadict(data, files, name)
        return None if not wkt else wkt_to_geom(wkt)

    def get_context(self, name, value, attrs=None, extra_context={}):
        context = super(LeafletMapWidget, self).get_context(name, value, attrs, extra_context)
        # Be careful, on form error, value is not a GEOSGeometry
        if value and not isinstance(value, basestring):
            value.transform(settings.API_SRID)
        context['update'] = bool(value)
        context['field'] = value
        context['fitextent'] = value is None
        return context


class MapEntityWidget(LeafletMapWidget):
    path_snapping = True
    
    def get_context(self, name, value, attrs=None, extra_context={}):
        context = super(MapEntityWidget, self).get_context(name, value, attrs, extra_context)
        context['min_snap_zoom'] = settings.MIN_SNAP_ZOOM
        context['path_snapping'] = self.path_snapping
        return context


class PointWidget(MapEntityWidget,
                  forms.gis.PointWidget):
    pass


class LineStringWidget(MapEntityWidget,
                       forms.gis.LineStringWidget):
    pass


class TopologyWidget(MapEntityWidget):
    """ A widget allowing to select a list of paths with start and end markers.
    Instead of building a Line geometry, this widget builds a Topology.
    """
    is_multipath = True
    
    def get_context(self, name, value, *args, **kwargs):
        if isinstance(value, basestring):
            try:
                value = self.deserialize(value)
            except ValueError:
                value = None
        topologyjson = ''
        if value:
            topologyjson = self.serialize(value)
        context = forms.Textarea.get_context(self, name, topologyjson, *args, **kwargs)
        context['module'] = 'map_%s' % name.replace('-', '_')
        context['is_multipath'] = self.is_multipath
        context['update'] = bool(value)
        context['field'] = value
        context['fitextent'] = value is None
        context['min_snap_zoom'] = settings.MIN_SNAP_ZOOM
        context['path_snapping'] = self.path_snapping
        return context

    def value_from_datadict(self, data, files, name):
        value = forms.Textarea.value_from_datadict(self, data, files, name)
        if not value:  # Empty value submitted
            return None
        try:
            return self.deserialize(value)
        except (ValueError, simplejson.JSONDecodeError):
            # TODO: raise validation error
            return None

    def deserialize(self, objstr):
        objdict = simplejson.loads(objstr)
        kind = objdict.get('kind')
        kind = TopologyMixinKind.objects.get(pk=int(kind)) if kind else TopologyMixin.get_kind()
        topology = TopologyMixinFactory.create(kind=kind)
        topology.offset = objdict.get('offset', 0.0)
        PathAggregation.objects.filter(topo_object=topology).delete()
        for aggrdict in objdict['paths']:
            try:
                path = Path.objects.get(pk=aggrdict['path'])
            except Path.DoesNotExist:
                # TODO raise ValueError(str(e))
                path = Path.objects.all()[0]
            aggrobj = PathAggregation(topo_object=topology,
                                   start_position=aggrdict.get('start', 0.0),
                                   end_position=aggrdict.get('end', 1.0),
                                   path=path)
            aggrobj.save()
        return topology

    def serialize(self, topology):
        paths = []
        for aggregation in topology.aggregations.all():
            paths.append(dict(start=aggregation.start_position,
                              end=aggregation.end_position,
                              path=aggregation.path.pk))
        objdict = dict(kind=topology.kind.pk,
                       offset=topology.offset,
                       paths=paths)
        return simplejson.dumps(objdict)


class PointTopologyWidget(TopologyWidget, PointWidget):
    """ A widget allowing to point a position with a marker. 
    Instead of building a Point geometry, this widget builds a Topology.
    """
    # TODO: test if point is returned, then compute topology from point
    pass


class PointLineTopologyWidget(PointTopologyWidget, TopologyWidget):
    pass
