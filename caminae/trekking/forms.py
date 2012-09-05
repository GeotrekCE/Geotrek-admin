from django.utils.translation import ugettext as _

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Submit, HTML

from caminae.core.forms import TopologyMixinForm
from caminae.core.widgets import PointWidget, LineTopologyWidget, PointTopologyWidget
from caminae.mapentity.widgets import SelectMultipleWithPop

from .models import Trek, POI, WebLink


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
            'published',
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
            'themes',
            'main_themes',
            'networks',
            'usages',
            'web_links',
            )

    def __init__(self, *args, **kwargs):
        super(TrekForm, self).__init__(*args, **kwargs)
        self.fields['topology'].widget = LineTopologyWidget()
        self.fields['web_links'].widget = SelectMultipleWithPop(
												choices=self.fields['web_links'].choices, 
												add_url=WebLink.get_add_url())

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


class WebLinkCreateFormPopup(forms.ModelForm):
    helper = FormHelper()

    def __init__(self, *args, **kwargs):
        super(WebLinkCreateFormPopup, self).__init__(*args, **kwargs)
        self.helper.form_action = self.instance.get_add_url()
        # Main form layout
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'name_fr',
            'name_en',
            'name_it',
            'url',
            'thumbnail',
            FormActions(
                HTML('<a href="#" class="btn" onclick="javascript:window.close();">%s</a>' % _("Cancel")),
                Submit('save_changes', _('Create'), css_class="btn-primary"),
                css_class="form-actions",
            )
        )
    class Meta:
        model = WebLink
        exclude = ('name', )
