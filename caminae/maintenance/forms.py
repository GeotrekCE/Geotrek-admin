from crispy_forms.layout import Field

from caminae.mapentity.forms import MapEntityForm
from caminae.core.fields import PointLineTopologyField

from .models import Intervention, Project


class InterventionForm(MapEntityForm):
    """ An intervention can be a Point or a Line """
    topology = PointLineTopologyField()

    modelfields = (
            'name',
            'structure',
            'date',
            'status',
            'type',
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
    geomfields = ('topology',)

    class Meta:
        model = Intervention
        exclude = ('deleted', 'geom', 'jobs')  # TODO


class ProjectForm(MapEntityForm):
    modelfields = (
            'name',
            'structure',
            'begin_year',
            'end_year',
            'constraint',
            'cost',
            Field('comments', css_class='input-xlarge'),
            'contractors',
            'project_owner',
            'project_manager',
            'founders',)
    geomfields = tuple()  # no geom field in project

    class Meta:
        model = Project
        exclude = ('deleted', 'founders',)  #TODO founders (inline form)
