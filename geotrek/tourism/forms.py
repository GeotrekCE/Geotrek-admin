from geotrek.common.forms import CommonForm

from .models import TouristicContent, TouristicEvent


class TouristicContentForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        fields = ['name', 'published', 'category', 'geom']
        model = TouristicContent


class TouristicEventForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        #fields = ['name', 'published', 'usage', 'geom']
        model = TouristicEvent
