from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import floppyforms as forms

from .models import TopologyMixin
from .widgets import TopologyWidget, PointLineTopologyWidget


class TopologyField(forms.CharField):
    """
    Instead of building a Point geometry, this field builds a Topology.
    """
    widget = TopologyWidget

    default_error_messages = {
        'invalid_topology': _(u'Topology is not valid.'),
    }

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return None
        try:
            return TopologyMixin.deserialize(value)
        except ValueError, e:
            raise ValidationError(self.error_messages['invalid_topology'] + unicode(e))



class PointLineTopologyField(TopologyField):
    widget = PointLineTopologyWidget
