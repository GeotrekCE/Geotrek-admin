from copy import deepcopy

from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Submit, HTML, Div, Fieldset
from leaflet.forms.widgets import LeafletWidget
from mapentity.widgets import SelectMultipleWithPop

from geotrek.common.forms import CommonForm
from geotrek.core.forms import TopologyForm
from geotrek.core.widgets import LineTopologyWidget, PointTopologyWidget
from .models import Trek, POI, WebLink, Service, ServiceType, OrderedTrekChild
from django.db import transaction
from django.core.urlresolvers import reverse


class TrekRelationshipForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TrekRelationshipForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout('id',
                                    'trek_a',
                                    'trek_b',
                                    'has_common_departure',
                                    'has_common_edge',
                                    'is_circuit_step',
                                    'DELETE')


TrekRelationshipFormSet = inlineformset_factory(Trek, Trek.related_treks.through,
                                                form=TrekRelationshipForm, fk_name='trek_a',
                                                extra=1)

if settings.TREKKING_TOPOLOGY_ENABLED:

    class BaseTrekForm(TopologyForm):
        def __init__(self, *args, **kwargs):
            super(BaseTrekForm, self).__init__(*args, **kwargs)
            self.fields['topology'].widget = LineTopologyWidget()
            self.fields['points_reference'].label = ''
            self.fields['points_reference'].widget.target_map = 'topology'
            self.fields['parking_location'].label = ''
            self.fields['parking_location'].widget.target_map = 'topology'

        class Meta(TopologyForm.Meta):
            model = Trek
else:

    class BaseTrekForm(CommonForm):
        geomfields = ['geom']

        def __init__(self, *args, **kwargs):
            super(BaseTrekForm, self).__init__(*args, **kwargs)
            self.fields['geom'].widget = LeafletWidget(attrs={'geom_type': 'LINESTRING'})
            self.fields['points_reference'].label = ''
            self.fields['points_reference'].widget.target_map = 'geom'
            self.fields['parking_location'].label = ''
            self.fields['parking_location'].widget.target_map = 'geom'

        class Meta(CommonForm.Meta):
            model = Trek
            fields = CommonForm.Meta.fields + ['geom']


class TrekForm(BaseTrekForm):
    children_trek = forms.ModelMultipleChoiceField(label=_(u"Children"),
                                                   queryset=Trek.objects.all(), required=False,
                                                   help_text=_(u"Select children in order"))
    hidden_ordered_children = forms.CharField(label=_(u"Hidden ordered children"),
                                              widget=forms.widgets.HiddenInput(),
                                              required=False)

    leftpanel_scrollable = False

    base_fieldslayout = [
        Div(
            HTML("""
            <ul class="nav nav-tabs">
                <li id="tab-main" class="active"><a href="#main" data-toggle="tab"><i class="icon-certificate"></i> %s</a></li>
                <li id="tab-advanced"><a href="#advanced" data-toggle="tab"><i class="icon-tasks"></i> %s</a></li>
            </ul>""" % (unicode(_("Main")), unicode(_("Advanced")))),
            Div(
                Div(
                    'name',
                    'review',
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
                    css_class="scrollable tab-pane active"
                ),
                Div(
                    'points_reference',
                    'disabled_infrastructure',
                    'advised_parking',
                    'parking_location',
                    'public_transport',
                    'advice',
                    'themes',
                    'networks',
                    'practice',
                    'accessibilities',
                    'web_links',
                    'information_desks',
                    'source',
                    'portal',
                    'children_trek',
                    'eid',
                    'eid2',
                    'hidden_ordered_children',
                    Fieldset(_("Related treks"),),
                    css_id="advanced",  # used in Javascript for activating tab if error
                    css_class="scrollable tab-pane"
                ),
                css_class="tab-content"
            ),
            css_class="tabbable"
        ),
    ]

    def __init__(self, *args, **kwargs):
        self.fieldslayout = deepcopy(self.base_fieldslayout)
        self.fieldslayout[0][1][0].append(HTML('<div class="controls">' + _('Insert service:') + ''.join(['<a class="servicetype" data-url="{url}" data-name={name}"><img src="{url}"></a>'.format(url=t.pictogram.url, name=t.name) for t in ServiceType.objects.all()]) + '</div>'))

        super(TrekForm, self).__init__(*args, **kwargs)

        self.fields['web_links'].widget = SelectMultipleWithPop(choices=self.fields['web_links'].choices,
                                                                add_url=WebLink.get_add_url())
        # Make sure (force) that name is required, in default language only
        self.fields['name_%s' % settings.LANGUAGE_CODE].required = True

        if not settings.TREK_POINTS_OF_REFERENCE_ENABLED:
            self.fields.pop('points_reference')
        else:
            # Edit points of reference with custom edition JavaScript class
            self.fields['points_reference'].widget.geometry_field_class = 'PointsReferenceField'

        self.fields['parking_location'].widget.geometry_field_class = 'ParkingLocationField'
        self.fields['duration'].widget.attrs['min'] = '0'

        # Since we use chosen() in trek_form.html, we don't need the default help text
        for f in ['themes', 'networks', 'accessibilities',
                  'web_links', 'information_desks', 'source', 'portal']:
            self.fields[f].help_text = ''

        if self.instance:
            queryset_children = OrderedTrekChild.objects.filter(parent__id=self.instance.pk)\
                                                        .order_by('order')
            # init multiple children field with data
            self.fields['children_trek'].queryset = Trek.objects.existing().exclude(pk=self.instance.pk)
            self.fields['children_trek'].initial = [c.child.pk for c in self.instance.trek_children.all()]

            # init hidden field with children order
            self.fields['hidden_ordered_children'].initial = ",".join(str(x) for x in queryset_children.values_list('child__id', flat=True))

    def clean_children_trek(self):
        """
        Check the trek is not parent and child at the same time
        """
        children = self.cleaned_data['children_trek']
        if children and self.instance and self.instance.trek_parents.exists():
            raise ValidationError(_(u"Cannot add children because this trek is itself a child."))
        for child in children:
            if child.trek_children.exists():
                raise ValidationError(_(u"Cannot use parent trek {name} as a child trek.".format(name=child.name)))
        return children

    def clean_duration(self):
        """For duration, an HTML5 "number" field is used. If the user fills an invalid
        number (like "2H40"), the browser will submit an empty value (!).
        Here we default to 0.0
        """
        duration = self.cleaned_data.get('duration')
        return 0.0 if duration is None else duration

    def save(self, *args, **kwargs):
        """
        Custom form save override - ordered children management
        """
        sid = transaction.savepoint()

        try:
            return_value = super(TrekForm, self).save(self, *args, **kwargs)
            ordering = []

            if self.cleaned_data['hidden_ordered_children']:
                ordering = self.cleaned_data['hidden_ordered_children'].split(',')

            order = 0

            # add and update
            for value in ordering:
                child, created = OrderedTrekChild.objects.get_or_create(parent=self.instance,
                                                                        child=Trek.objects.get(pk=value))
                child.order = order
                child.save()
                order += 1

            # delete
            new_list_children = self.cleaned_data['children_trek'].values_list('pk', flat=True)

            for child_relation in self.instance.trek_children.all():
                # if existant child not in selection, deletion
                if child_relation.child_id not in new_list_children:
                    child_relation.delete()

            transaction.savepoint_commit(sid)
            return return_value

        except Exception as exc:
            transaction.savepoint_rollback(sid)
            raise exc

    class Meta(BaseTrekForm.Meta):
        fields = BaseTrekForm.Meta.fields + \
            ['name', 'review', 'published', 'is_park_centered', 'departure',
             'arrival', 'duration', 'difficulty', 'route', 'ambiance',
             'access', 'description_teaser', 'description', 'points_reference',
             'disabled_infrastructure', 'advised_parking', 'parking_location',
             'public_transport', 'advice', 'themes', 'networks', 'practice',
             'accessibilities', 'web_links', 'information_desks', 'source', 'portal',
             'children_trek', 'eid', 'eid2', 'hidden_ordered_children', 'structure']


if settings.TREKKING_TOPOLOGY_ENABLED:

    class BasePOIForm(TopologyForm):
        def __init__(self, *args, **kwargs):
            super(BasePOIForm, self).__init__(*args, **kwargs)
            self.fields['topology'].widget = PointTopologyWidget()

        class Meta(TopologyForm.Meta):
            model = POI

else:

    class BasePOIForm(CommonForm):
        geomfields = ['geom']

        def __init__(self, *args, **kwargs):
            super(BasePOIForm, self).__init__(*args, **kwargs)
            self.fields['geom'].widget = LeafletWidget(attrs={'geom_type': 'POINT'})

        class Meta(CommonForm.Meta):
            model = POI
            fields = CommonForm.Meta.fields + ['geom']


class POIForm(BasePOIForm):
    fieldslayout = [
        Div(
            'name',
            'review',
            'published',
            'type',
            'description',
        )
    ]

    class Meta(BasePOIForm.Meta):
        fields = BasePOIForm.Meta.fields + ['name', 'description', 'type', 'published', 'review', 'structure']


if settings.TREKKING_TOPOLOGY_ENABLED:

    class BaseServiceForm(TopologyForm):
        def __init__(self, *args, **kwargs):
            super(BaseServiceForm, self).__init__(*args, **kwargs)
            self.fields['topology'].widget = PointTopologyWidget()

        class Meta(TopologyForm.Meta):
            model = Service

else:

    class BaseServiceForm(CommonForm):
        geomfields = ['geom']

        def __init__(self, *args, **kwargs):
            super(BaseServiceForm, self).__init__(*args, **kwargs)
            self.fields['geom'].widget = LeafletWidget(attrs={'geom_type': 'POINT'})

        class Meta(CommonForm.Meta):
            model = Service
            fields = CommonForm.Meta.fields + ['geom']


class ServiceForm(BaseServiceForm):
    fieldslayout = [
        Div(
            'type',
            'review',
            'eid',
        )
    ]

    class Meta(BaseServiceForm.Meta):
        fields = BaseServiceForm.Meta.fields + ['type', 'structure']


class WebLinkCreateFormPopup(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(WebLinkCreateFormPopup, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = self.instance.get_add_url()
        # Main form layout
        # Adds every name field explicitly (name_fr, name_en, ...)
        self.helper.form_class = 'form-horizontal'
        arg_list = ['name_{0}'.format(l[0]) for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']]
        arg_list += ['url', 'category', FormActions(
            HTML('<a href="#" class="btn" onclick="javascript:window.close();">%s</a>' % _("Cancel")),
            Submit('save_changes', _('Create'), css_class="btn-primary"),
            css_class="form-actions",
        )]
        self.helper.layout = Layout(*arg_list)

    class Meta:
        model = WebLink
        fields = ['name_{0}'.format(l[0]) for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']] + \
                 ['url', 'category']


class SyncRandoForm(forms.Form):
    """
    Sync Rando View Form
    """

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_id = 'form-sync'
        helper.form_action = reverse('trekking:sync_randos')
        helper.form_class = 'search'
        # submit button with boostrap attributes, disabled by default
        helper.add_input(Submit('sync-web', _("Launch Sync"),
                                **{'data-toggle': "modal",
                                   'data-target': "#confirm-submit",
                                   'disabled': 'disabled'}))

        return helper
