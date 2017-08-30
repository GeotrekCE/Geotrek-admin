from .models import SensitiveArea
from geotrek.common.forms import CommonForm


class SensitiveAreaForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        fields = ['species', 'published', 'geom']
        model = SensitiveArea
