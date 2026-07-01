import json
import logging

from django import forms
from django.contrib.gis.forms import GeometryField
from django.contrib.gis.geos import LineString, Point
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from mapentity.widgets import MapWidget

from .models import Topology
from .widgets import GeotrekMapWidget, LineTopologyWidget

logger = logging.getLogger(__name__)


class TopologyField(forms.CharField):
    """Instead of building a geometry, this field builds a Topology."""

    widget = None

    default_error_messages = {
        "empty_topology": _("Topology is empty."),
        "invalid_topology": _("Topology is not valid."),
        "unknown_topology": _("Topology %s does not exist."),
    }

    def clean(self, value):
        if value in validators.EMPTY_VALUES:
            if self.required:
                raise ValidationError(self.error_messages["empty_topology"])
            return None
        try:
            return Topology.deserialize(value)
        except Topology.DoesNotExist:
            raise ValidationError(self.error_messages["unknown_topology"] % value)
        except ValueError as e:
            logger.warning("User input error: %s", e)
            raise ValidationError(self.error_messages["invalid_topology"])


class PointTopoGeomField(TopologyField):
    """This field builds a point topology or geometry from a point geometry, drawn using MapWidget."""

    widget = MapWidget(
        geom_type="POINT",
        attrs={
            "snapping_config": {
                "enabled": True,
                "layers": ["core.Path"],
                "snap_distance": 20,
            }
        },
    )

    def clean(self, value):
        if value in validators.EMPTY_VALUES:
            if self.required:
                raise ValidationError(self.error_messages["empty_topology"])
            return None
        try:
            objdict = json.loads(value)
            coords = objdict.get("coordinates")
            if coords is None:
                raise ValidationError(self.error_messages["invalid_topology"])
            return Topology.deserialize(f'{{"lat": {coords[1]}, "lng": {coords[0]}}}')
        except Topology.DoesNotExist:
            raise ValidationError(self.error_messages["unknown_topology"] % value)
        except ValueError as e:
            logger.warning("User input error: %s", e)
            raise ValidationError(self.error_messages["invalid_topology"])


class LineTopologyField(TopologyField):
    """This fields builds a line topology."""
    widget = LineTopologyWidget()


class PointLineTopoGeomField(GeometryField):
    """
    This fields builds either:
      - a point geometry or point topology (depending on whether paths exist);
      - a line geometry.
    """
    geom_type = "GEOMETRY"
    widget = GeotrekMapWidget(
        attrs={
            "allowed_types": ["POINT", "LINESTRING"],
            "geom_type": "GEOMETRY",
            "snapping_config": {
                "enabled": True,
                "layers": ["core.Path"],
                "snap_distance": 20,
            }
        }
    )

    def clean(self, value):
        """
        If the geometry is a line, return it as a geometry.
        If it is a point, return either a topology or a geometry.
        """
        if value in validators.EMPTY_VALUES:
            if self.required:
                raise ValidationError(self.error_messages["empty_topology"])
            return None
        try:
            raw_geom = json.loads(value)
            geom = super().clean(value)
            if isinstance(geom, LineString):
                return geom
            if not isinstance(geom, Point):
                raise ValidationError(_("The geometry should either be a point or a linestring."))
            coords = raw_geom.get("coordinates")
            if coords is None:
                raise ValidationError(self.error_messages["invalid_topology"])
            return Topology.deserialize(f'{{"lat": {coords[1]}, "lng": {coords[0]}}}')
        except Topology.DoesNotExist:
            raise ValidationError(self.error_messages["unknown_topology"] % value)
        except ValueError as e:
            logger.warning("User input error: %s", e)
            raise ValidationError(self.error_messages["invalid_topology"])

