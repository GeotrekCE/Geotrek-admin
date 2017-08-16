from .models import SensitiveArea
from geotrek.common.forms import CommonForm


class SensitiveAreaForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        fields = ['species', 'geom']
        model = SensitiveArea
