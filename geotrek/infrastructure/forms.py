from crispy_forms.layout import Div
from django import forms
from django.utils.translation import gettext_lazy as _

from geotrek.core.mixins.forms import PointLineTopologyFormMixin

from .models import Infrastructure


class InfrastructureForm(PointLineTopologyFormMixin):
    implantation_year = forms.IntegerField(label=_("Implantation year"), required=False)

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
