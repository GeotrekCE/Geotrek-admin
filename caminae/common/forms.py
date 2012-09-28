from django import forms as django_forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ForeignKey, ManyToManyField, FieldDoesNotExist

import floppyforms as forms
from crispy_forms.layout import Layout, Submit, Div, Button
from crispy_forms.bootstrap import FormActions
from tinymce.widgets import TinyMCE
from modeltranslation.translator import translator, NotRegistered

from caminae.authent.models import (default_structure, StructureRelated,
                                    StructureRelatedQuerySet)
from caminae.mapentity.forms import MapEntityForm


class CommonForm(MapEntityForm):
    formfield_callback = lambda f: CommonForm.make_tinymce_widget(f)

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
        super(CommonForm, self).__init__(*args, **kwargs)

        # Check if structure is present, if so, use hidden input
        if 'structure' in self.fields:
            self.fields['structure'].widget = forms.HiddenInput()
            # On entity creation, use user's structure
            if not self.instance or not self.instance.pk:
                structure = default_structure()
                if self.user:
                    structure = self.user.profile.structure
                self.fields['structure'].initial = structure

        # Filter structured choice fields according to user's structure
        for name, field in self.fields.items():
            if isinstance(field, django_forms.models.ModelChoiceField):
                try:
                    modelfield = self.instance._meta.get_field(name)
                except FieldDoesNotExist:
                    # be careful but custom form fields, not in model
                    modelfield = None
                if isinstance(modelfield, (ForeignKey, ManyToManyField)):
                    model = modelfield.related.parent_model
                    if issubclass(model, StructureRelated):
                        field.queryset = StructureRelatedQuerySet.queryset_for_user(field.queryset, self.user)

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

