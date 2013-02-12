from django.utils.translation import ugettext as _
from django.conf import settings
from django.forms.models import inlineformset_factory

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Submit, HTML, Div, Fieldset

from caminae.core.forms import TopologyForm
from caminae.mapentity.widgets import PointWidget
from caminae.core.widgets import LineTopologyWidget, PointTopologyWidget
from caminae.mapentity.widgets import SelectMultipleWithPop

from .models import Trek, POI, WebLink


class TrekRelationshipForm(forms.ModelForm):
    helper = FormHelper()
    def __init__(self, *args, **kwargs):
        super(TrekRelationshipForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        self.helper.layout = Layout('id',
                                    'trek_a',
                                    'trek_b',
                                    'has_common_departure',
                                    'has_common_edge',
                                    'is_circuit_step')

TrekRelationshipFormSet = inlineformset_factory(Trek, Trek.related_treks.through, form=TrekRelationshipForm, fk_name='trek_a', extra=1)


class TrekForm(TopologyForm):
    parking_location = forms.gis.GeometryField(widget=PointWidget, required=False)

    modelfields = (
        Div(
            HTML("""
            <ul class="nav nav-tabs">
                <li id="tab-main" class="active"><a href="#main" data-toggle="tab"><i class="icon-certificate"></i> %s</a></li>
                <li id="tab-advanced"><a href="#advanced" data-toggle="tab"><i class="icon-tasks"></i> %s</a></li>
            </ul>""" % (_("Main"), _("Advanced"))),
            Div(
                Div(
                    'name',
                    'published',
                    'is_park_centered',
                    'departure',
                    'arrival',
                    'duration',
                    'difficulty',
                    'route',
                    'ambiance',
                    'access',
                    'description_teaser',
                    'description',
                    css_id="main",
                    css_class="tab-pane active"
                ),
                Div('disabled_infrastructure',
                    'advised_parking',
                    'parking_location',
                    'public_transport',
                    'advice',
                    'themes',
                    'networks',
                    'usages',
                    'web_links',
                    Fieldset(_("Related treks"),),
                    css_id="advanced",  # used in Javascript for activating tab if error
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
        # Make sure (force) that name is required, in default language only
        self.fields['name_%s' % settings.LANGUAGE_CODE].required = True

    class Meta(TopologyForm.Meta):
        model = Trek
        exclude = TopologyForm.Meta.exclude + ('related_treks',)


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
        arg_list += ['url', 'category', FormActions(
            HTML('<a href="#" class="btn" onclick="javascript:window.close();">%s</a>' % _("Cancel")),
            Submit('save_changes', _('Create'), css_class="btn-primary"),
            css_class="form-actions",
        )]
        self.helper.layout = Layout(*arg_list)
    class Meta:
        model = WebLink
        exclude = ('name',)
