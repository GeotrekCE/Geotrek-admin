from django import forms as django_forms
from django.utils.translation import ugettext_lazy as _

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Button
from crispy_forms.bootstrap import FormActions
from tinymce.widgets import TinyMCE


class MapEntityForm(forms.ModelForm):
    formfield_callback = lambda f: MapEntityForm.make_tinymce_widget(f)

    pk = forms.Field(required=False, widget=forms.Field.hidden_widget)
    model = forms.Field(required=False, widget=forms.Field.hidden_widget)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    
    modelfields = tuple()
    geomfields = tuple()
    actions = FormActions(
        Button('cancel', _('Cancel'), ),
        Submit('save_changes', _('Save changes'), css_class="btn-primary offset1"),
        css_class="form-actions span11",
    )

    @staticmethod
    def make_tinymce_widget(f):
        formfield = f.formfield()
        if formfield and isinstance(formfield.widget, (forms.widgets.Textarea, 
                                                       django_forms.widgets.Textarea)):
            formfield.widget = TinyMCE()
        return formfield

    def __init__(self, *args, **kwargs):
        super(MapEntityForm, self).__init__(*args, **kwargs)
        # Generic behaviour
        if self.instance.pk:
            self.helper.form_action = self.instance.get_update_url()
        else:
            self.helper.form_action = self.instance.get_add_url()
        self.fields['pk'].initial = self.instance.pk
        self.fields['model'].initial = self.instance._meta.module_name
        
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
        self.helper.layout = Layout(
            leftpanel,
            rightpanel,
            self.actions
        )
