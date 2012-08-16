from django.contrib.gis.geos import Point, LineString

import floppyforms as forms

from caminae.mapentity.forms import MapEntityForm
from caminae.core.forms import TopologyMixinForm
from caminae.core.widgets import PointWidget, MultiPathWidget

from .models import Trek, POI


class TrekForm(MapEntityForm):
    parking_location = forms.gis.GeometryField(widget=PointWidget)
    geom = forms.gis.GeometryField(widget=MultiPathWidget)

    modelfields = (
            'name_fr',
            'name_it',
            'name_en',
            'departure_fr',
            'departure_it',
            'departure_en',
            'arrival_fr',
            'arrival_en',
            'arrival_it',
            'validated',
            'difficulty',
            'route',
            'destination',
            'description_teaser_fr',
            'description_teaser_it',
            'description_teaser_en',
            'description_fr',
            'description_it',
            'description_en',
            'ambiance_fr',
            'ambiance_it',
            'ambiance_en',
            'disabled_infrastructure_fr',
            'disabled_infrastructure_it',
            'disabled_infrastructure_en',
            'duration',
            'is_park_centered',
            'is_transborder',
            'advised_parking',
            'parking_location',
            'public_transport',
            'advice_fr',
            'advice_it',
            'advice_en',
            'networks',
            'usages',
            'web_links',
            )
    geomfields = ('geom', )

    def save(self, commit=True, **kwargs):
        obj = super(TrekForm, self).save(commit=False, **kwargs)
        obj.geom = LineString(Point(0, 0, 0), Point(1, 1, 0))  # TODO: list of paths
        if commit:
            obj.save()
        return obj

    class Meta:
        model = Trek
        exclude = ('deleted', 'paths', 'length') + ('name', 'departure', 'arrival', 
                   'description', 'description_teaser', 'ambiance', 'advice',
                   'disabled_infrastructure',)  # TODO


class POIForm(TopologyMixinForm):
    geom = forms.gis.GeometryField(widget=PointWidget)

    modelfields = (
            'name_fr',
            'name_it',
            'name_en',
            'description_fr',
            'description_it',
            'description_en',
            'type',
            )

    class Meta(TopologyMixinForm.Meta):
        model = POI
        exclude = TopologyMixinForm.Meta.exclude + ('name', 'description')  # TODO: topology editor
