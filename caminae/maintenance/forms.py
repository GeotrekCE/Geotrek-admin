import floppyforms as forms
from crispy_forms.layout import Field

from caminae.core.forms import ModuleForm
from caminae.core.widgets import PointOrLineStringWidget

from .models import Intervention


class InterventionForm(ModuleForm):
    geom = forms.gis.GeometryField(widget=PointOrLineStringWidget)

    fields = (
            'name',
            'date',
            'status',
            'typology',
            'disorders',
            Field('comments', css_class='input-xlarge'),
            'in_maintenance',
            'length',
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
