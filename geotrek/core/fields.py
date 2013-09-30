import logging
import json

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.gis.geos import Point, LineString

import floppyforms as forms
from mapentity.helpers import wkt_to_geom

from .models import Topology, Path
from .widgets import PointLineTopologyWidget, SnappedLineStringWidget


logger = logging.getLogger(__name__)


class TopologyField(forms.CharField):
    """
    Instead of building a Point geometry, this field builds a Topology.
    """
    widget = PointLineTopologyWidget

    default_error_messages = {
        'empty_topology': _(u'Topology is empty.'),
        'invalid_topology': _(u'Topology is not valid.'),
        'unknown_topology': _(u'Topology %s does not exist.'),
    }

    def clean(self, value):
        if value in validators.EMPTY_VALUES:
            if self.required:
                raise ValidationError(self.error_messages['empty_topology'])
            return None
        try:
            return Topology.objects.get(pk=int(value))
        except Topology.DoesNotExist:
            raise ValidationError(self.error_messages['unknown_topology'] % value)
        except ValueError:
            pass  # value is not integer, thus should be deserialized
        try:
            return Topology.deserialize(value)
        except ValueError as e:
            logger.warning("User input error: %s" % e)
            raise ValidationError(self.error_messages['invalid_topology'])


class SnappedLineStringField(forms.gis.LineStringField):
    """
    It's a LineString field, with additional information about snapped vertices.
    """
    dim = 2
    widget = SnappedLineStringWidget

    default_error_messages = {
        'invalid_snap_line': _(u'Linestring invalid snapping.'),
    }

    def clean(self, value):
        if value in validators.EMPTY_VALUES:
            return None
        try:
            value = json.loads(value)
            geom = value.get('geom')
            if geom is None:
                raise ValueError("No geom found in JSON")
            geom = wkt_to_geom(geom)
            if geom is None:
                raise ValueError("Invalid WKT in JSON")
            geom.transform(settings.SRID)

            # We have the list of snapped paths, we use them to modify the
            # geometry vertices
            snaplist = value.get('snap', [])
            if geom.num_coords != len(snaplist):
                raise ValueError("Snap list length != %s (%s)" % (geom.num_coords, snaplist))
            paths_pk = [(i, p) for (i, p) in enumerate(snaplist)]
            paths = [(i, Path.objects.get(pk=pk)) for (i, pk) in paths_pk if pk is not None]
            paths = dict(paths)
            coords = list(geom.coords)
            for i, vertex in enumerate(coords):
                path = paths.get(i)
                if path:
                    snap = path.snap(Point(*vertex, srid=geom.srid))
                    vertex = snap.coords
                coords[i] = vertex
            return LineString(*coords, srid=settings.SRID)
        except (TypeError, Path.DoesNotExist, ValueError) as e:
            logger.warning("User input error: %s" % e)
            raise ValidationError(self.error_messages['invalid_snap_line'])
