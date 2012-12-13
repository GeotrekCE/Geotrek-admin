from django.utils.translation import ugettext as _
from django.conf import settings

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Submit, HTML, Div

from caminae.core.forms import TopologyForm
from caminae.mapentity.widgets import PointWidget
from caminae.core.widgets import LineTopologyWidget, PointTopologyWidget
from caminae.mapentity.widgets import SelectMultipleWithPop

from .models import Trek, POI, WebLink


class TrekForm(TopologyForm):
    parking_location = forms.gis.GeometryField(widget=PointWidget)

    modelfields = (
        Div(
            HTML("""
            <ul class="nav nav-tabs">
                <li class="active"><a href="#main" data-toggle="tab"><i class="icon-certificate"></i> %s</a></li>
                <li><a href="#advanced" data-toggle="tab"><i class="icon-tasks"></i> %s</a></li>
            </ul>""" % (_("Main"), _("Advanced"))),
            Div(
                Div(
                    'name',
                    'published',
                    'departure',
                    'arrival',
                    'duration',
                    'difficulty',
                    'route',
                    'description_teaser',
                    'description',
                    'is_park_centered',
                    css_id="main",
                    css_class="tab-pane active"
                ),
                Div('ambiance',
                    'disabled_infrastructure',
                    'advised_parking',
                    'parking_location',
                    'public_transport',
                    'advice',
                    'themes',
                    'networks',
                    'usages',
                    'web_links',
                    css_id="advanced",
                    css_class="tab-pane"
                ),
                css_class="tab-content"
            ),
            css_class="tabbable"
        ),
    )

    def __init__(self, *args, **kwargs):
        super(TrekForm, self).__init__(*args, **kwargs)
        self.fields['topology'].widget = LineTopologyWidget()
        self.fields['web_links'].widget = SelectMultipleWithPop(
                                                choices=self.fields['web_links'].choices, 
                                                add_url=WebLink.get_add_url())

    class Meta(TopologyForm.Meta):
        model = Trek


class POIForm(TopologyForm):
    modelfields = (
            'name',
            'description',
            'type',
            )

    def __init__(self, *args, **kwargs):
        super(POIForm, self).__init__(*args, **kwargs)
        self.fields['topology'].widget = PointTopologyWidget()

    class Meta(TopologyForm.Meta):
        model = POI


class WebLinkCreateFormPopup(forms.ModelForm):
    helper = FormHelper()

    def __init__(self, *args, **kwargs):
        super(WebLinkCreateFormPopup, self).__init__(*args, **kwargs)
        self.helper.form_action = self.instance.get_add_url()
        # Main form layout
        self.helper.form_class = 'form-horizontal'
        arg_list = ['name_{0}'.format(l[0]) for l in settings.LANGUAGES]
        arg_list += ['url', 'thumbnail', FormActions(
            HTML('<a href="#" class="btn" onclick="javascript:window.close();">%s</a>' % _("Cancel")),
            Submit('save_changes', _('Create'), css_class="btn-primary"),
            css_class="form-actions",
        )]
        self.helper.layout = Layout(*arg_list)
    class Meta:
        model = WebLink
        exclude = ('name',)
