import json
import logging

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from mapentity.widgets import MapWidget

from .models import Topology
from .widgets import PointLineTopologyWidget

logger = logging.getLogger(__name__)


class TopologyField(forms.CharField):
    """Instead of building a geometry, this field builds a Topology."""

    widget = PointLineTopologyWidget

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


class PointTopologyField(TopologyField):
    """This field builds a topology from a point geometry, drawn using MapWidget."""
    widget = MapWidget(
        geom_type="POINT",
        attrs={
            "snapping_config": {
                "enabled": True,
                "layers": ["core.Path"],
                "snap_distance": 20,
            }
        }
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
