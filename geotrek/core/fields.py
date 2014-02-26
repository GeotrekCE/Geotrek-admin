import logging
import json

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.conf import settings
from django.contrib.gis.forms.fields import LineStringField
from django.contrib.gis.geos import fromstr, Point, LineString

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
            return Topology.deserialize(value)
        except Topology.DoesNotExist:
            raise ValidationError(self.error_messages['unknown_topology'] % value)
        except ValueError as e:
            logger.warning("User input error: %s" % e)
            raise ValidationError(self.error_messages['invalid_topology'])


class SnappedLineStringField(LineStringField):
    """
    It's a LineString field, with additional information about snapped vertices.
    """
    widget = SnappedLineStringWidget

    default_error_messages = {
        'invalid_snap_line': _(u'Linestring invalid snapping.'),
    }

    def clean(self, value):
        """
        A serialized dict is received, with ``geom`` and ``snaplist``.
        We use ``snaplist`` to snap geometry vertices.
        """
        if value in validators.EMPTY_VALUES:
            return super(SnappedLineStringField, self).clean(value)
        try:
            value = json.loads(value)
            geom = value.get('geom')
            if geom is None:
                raise ValueError("No geom found in JSON")

            if geom in validators.EMPTY_VALUES:
                return super(SnappedLineStringField, self).clean(value)

            # Geometry is like usual
            geom = fromstr(geom)
            if geom is None:
                raise ValueError("Invalid geometry in JSON")
            geom.srid = settings.API_SRID
            geom.transform(settings.SRID)

            # We have the list of snapped paths, we use them to modify the
            # geometry vertices
            snaplist = value.get('snap', [])
            if geom.num_coords != len(snaplist):
                raise ValueError("Snap list length != %s (%s)" % (geom.num_coords, snaplist))
            paths = [Path.objects.get(pk=pk) if pk is not None else None
                     for pk in snaplist]
            coords = list(geom.coords)
            for i, (vertex, path) in enumerate(zip(coords, paths)):
                if path:
                    # Snap vertex on path
                    snap = path.snap(Point(*vertex, srid=geom.srid))
                    coords[i] = snap.coords
            return LineString(*coords, srid=settings.SRID)
        except (TypeError, Path.DoesNotExist, ValueError) as e:
            logger.warning("User input error: %s" % e)
            raise ValidationError(self.error_messages['invalid_snap_line'])
