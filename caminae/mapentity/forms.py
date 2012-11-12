from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import forms as django_forms

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Button
from crispy_forms.bootstrap import FormActions
from tinymce.widgets import TinyMCE
from modeltranslation.translator import translator, NotRegistered


class MapEntityForm(forms.ModelForm):
    formfield_callback = lambda f: MapEntityForm.make_tinymce_widget(f)

    modelfields = tuple()
    geomfields = tuple()
    actions = FormActions(
        Button('cancel', _('Cancel'), ),
        Submit('save_changes', _('Save changes'), css_class="btn-primary offset1"),
        css_class="form-actions span11",
    )

    pk = forms.Field(required=False, widget=forms.Field.hidden_widget)
    model = forms.Field(required=False, widget=forms.Field.hidden_widget)

    helper = FormHelper()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MapEntityForm, self).__init__(*args, **kwargs)

        # Generic behaviour
        if self.instance.pk:
            self.helper.form_action = self.instance.get_update_url()
        else:
            self.helper.form_action = self.instance.get_add_url()
        self.fields['pk'].initial = self.instance.pk
        self.fields['model'].initial = self.instance._meta.module_name

        # Expand i18n fields
        try:
            # Obtain model translation options
            mto = translator.get_options_for_model(self._meta.model)
        except NotRegistered:
            # No translation field on this model, nothing to do
            pass
        else:
            self.modelfields = list(self.modelfields) # Switch to mutable sequence
            for f in mto.fields:
                self.fields.pop(f)
                if f in self.modelfields:
                    # Replace i18n field by dynamic l10n fields
                    i = self.modelfields.index(f)
                    self.modelfields[i:i+1] = ['{0}_{1}'.format(f, l[0])
                                             for l in settings.LANGUAGES]
            self.modelfields = tuple(self.modelfields) # Switch back to unmutable sequence

        # Get fields from subclasses
        fields = ('pk','model') + self.modelfields
        leftpanel = Div(
            *fields,
            css_class="span3"
        )

        rightpanel = Div(
            *self.geomfields,
            css_class="span8"
        )
        
        # Main form layout
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            leftpanel,
            rightpanel,
            self.actions
        )

    @staticmethod
    def make_tinymce_widget(f):
        formfield = f.formfield()
        if formfield and isinstance(formfield.widget, (forms.widgets.Textarea, 
                                                       django_forms.widgets.Textarea)):
            formfield.widget = TinyMCE()
        return formfield
