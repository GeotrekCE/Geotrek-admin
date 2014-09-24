from geotrek.common.forms import CommonForm

from .models import TouristicContent


class TouristicContentForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        fields = ['name', 'category', 'geom']
        model = TouristicContent
