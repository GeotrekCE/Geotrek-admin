import floppyforms as forms
from crispy_forms.layout import Field

from caminae.core.forms import MapEntityForm
from caminae.core.widgets import PointOrLineStringWidget

from .models import Intervention


class InterventionForm(MapEntityForm):
    geom = forms.gis.GeometryField(widget=PointOrLineStringWidget)

    modelfields = (
            'name',
            'structure',
            'date',
            'status',
            'typology',
            'disorders',
            Field('comments', css_class='input-xlarge'),
            'in_maintenance',
            'length',
            'height',
            'width',
            'area',
            'slope',
            'material_cost',
            'heliport_cost',
            'subcontract_cost',
            'stake',
            'project',)
    geomfields = ('geom',)

    class Meta:
        model = Intervention
        exclude = ('deleted', 'topologies', 'jobs') # TODO
