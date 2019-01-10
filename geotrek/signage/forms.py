from django.conf import settings
from django.db.models import Q
from geotrek.core.widgets import PointTopologyWidget
from geotrek.infrastructure.forms import BaseInfrastructureForm

from .models import Signage, SignageType


class SignageForm(BaseInfrastructureForm):
    def __init__(self, *args, **kwargs):
        super(SignageForm, self).__init__(*args, **kwargs)

        if not settings.SIGNAGE_LINE_ENABLED:
            modifiable = self.fields['topology'].widget.modifiable
            self.fields['topology'].widget = PointTopologyWidget()
            self.fields['topology'].widget.modifiable = modifiable

        if self.instance.pk:
            structure = self.instance.structure
        else:
            structure = self.user.profile.structure
        self.fields['type'].queryset = SignageType.objects.filter(Q(structure=structure) | Q(structure=None))
        self.fields['condition'].queryset = structure.infrastructurecondition_set.all()

    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
