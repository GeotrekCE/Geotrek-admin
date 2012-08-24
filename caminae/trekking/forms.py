import floppyforms as forms

from caminae.core.forms import TopologyMixinForm
from caminae.core.widgets import PointWidget, LineTopologyWidget, PointTopologyWidget

from .models import Trek, POI


class TrekForm(TopologyMixinForm):
    parking_location = forms.gis.GeometryField(widget=PointWidget)

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

    def __init__(self, *args, **kwargs):
        super(TrekForm, self).__init__(*args, **kwargs)
        self.fields['topology'].widget = LineTopologyWidget()

    class Meta(TopologyMixinForm.Meta):
        model = Trek
        exclude = TopologyMixinForm.Meta.exclude + ('name', 'departure', 'arrival', 
                   'description', 'description_teaser', 'ambiance', 'advice',
                   'disabled_infrastructure',)  # TODO, fix modeltranslations


class POIForm(TopologyMixinForm):
    modelfields = (
            'name_fr',
            'name_it',
            'name_en',
            'description_fr',
            'description_it',
            'description_en',
            'type',
            )

    def __init__(self, *args, **kwargs):
        super(POIForm, self).__init__(*args, **kwargs)
        self.fields['topology'].widget = PointTopologyWidget()

    class Meta(TopologyMixinForm.Meta):
        model = POI
        exclude = TopologyMixinForm.Meta.exclude + ('name', 'description')  # TODO: topology editor
