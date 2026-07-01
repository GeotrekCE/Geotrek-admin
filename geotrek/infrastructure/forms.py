from crispy_forms.layout import Div

from geotrek.core.mixins.forms import PointLineTopologyFormMixin

from .models import Infrastructure


class InfrastructureForm(PointLineTopologyFormMixin):
    fieldslayout = [
        Div(
            "structure",
            "name",
            "description",
            "accessibility",
            "type",
            "conditions",
            "access",
            "implantation_year",
            "usage_difficulty",
            "maintenance_difficulty",
            "published",
        )
    ]

    class Meta(PointLineTopologyFormMixin.Meta):
        model = Infrastructure
        fields = [
            *PointLineTopologyFormMixin.Meta.fields,
            "structure",
            "name",
            "type",
            "description",
            "access",
            "implantation_year",
            "published",
            "accessibility",
            "maintenance_difficulty",
            "usage_difficulty",
            "conditions",
        ]
